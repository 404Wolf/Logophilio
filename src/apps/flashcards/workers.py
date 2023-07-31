from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from uuid import uuid1

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.db import connection
import base64

from .renderer.renderer import FlashcardRenderer
from ..flashcards.models import Flashcard, FlashcardStyle
from ..words.models import WordImageConfig, Word, WordImage

imageGenLock = Lock()


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
    images = list(WordImage.objects.filter(word=word, config=imgConfig))

    def _createImage():
        image = WordImage.generated(word, imgConfig)
        return image

    imageCreators = []
    with ThreadPoolExecutor() as executor:
        for i in range(count - len(images)):
            imageCreators.append(executor.submit(_createImage))
        for imageCreator in as_completed(imageCreators):
            image = imageCreator.result()
            image.save()
            assert image.word == word
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

    flashcard = Flashcard(
        word=word,
        style=style,
    )

    imageGenLock.acquire()
    renderer = FlashcardRenderer(flashcard, images)
    renderedFront = base64.b64decode(renderer.rendered("front"))
    renderedBack = base64.b64decode(renderer.rendered("back"))
    flashcard.front = ContentFile(renderedFront, f"{str(uuid1())}.pdf")
    flashcard.back = ContentFile(renderedBack, f"{str(uuid1())}.pdf")
    imageGenLock.release()

    flashcard.save()
    return flashcard
