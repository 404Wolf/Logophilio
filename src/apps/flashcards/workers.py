from base64 import b64decode
from concurrent.futures import ThreadPoolExecutor, as_completed
from uuid import uuid1

from botocore.docs.bcdoc import style
from django.core.files.base import ContentFile

from ..flashcards.models import Flashcard, FlashcardStyle
from ..words.models import WordImageConfig, Word, WordImage


def generateImages(
    word: Word, count: int, imgConfig: WordImageConfig
) -> list[WordImage]:
    """
    Generate images for a given word using a given image config preset.

    Args:
        word: The Word object to generate images for.
        count: The number of images to generate.
        imgConfig: The image configuration to use for generating and templating prompts.

    Returns:
        list[WordImage]: A list of word images.
    """
    assert isinstance(
        word, Word
    ), f"Image generation requires a Word model instance; got {type(word)}"
    images = list(WordImage.objects.filter(word=word))
    with ThreadPoolExecutor() as executor:
        imageCreators = []
        for i in range(count - len(images)):
            imageCreators.append(executor.submit(WordImage.generated, word, imgConfig))
        for imageCreator in as_completed(imageCreators):
            image = imageCreator.result()
            images.append(image)
    return images


def generateFlashcard(
    word: Word, style: FlashcardStyle, images: list[WordImage]
) -> Flashcard:
    """
    Generate an English vocab flashcard.

    Args:
        word: The word and its data to use for flashcard generation.
        style: The style to use for flashcard generation.
        images: The images to use for flashcard generation. Should be of length
            `style.imgCount("front") + style.imgCount("back")` or greater.

    Returns:
        A Flashcard model type object.
    """
    assert isinstance(
        word, Word
    ), f"Flashcard generation requires a Word model instance; got {type(word)}."
    frontImgCount = style.imgCount("front")
    flashcard = Flashcard(
        word=word,
        style=style,
    )
    flashcard.front = ContentFile(
        b64decode(
            flashcard.rendered(style.template("front"), images[:frontImgCount])
        ),
        name=f"{str(uuid1())}.pdf",
    )
    flashcard.back = ContentFile(
        b64decode(
            flashcard.rendered(style.template("back"), images[frontImgCount:])
        ),
        name=f"{str(uuid1())}.pdf",
    )
    return flashcard