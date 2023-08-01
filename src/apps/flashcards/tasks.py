import base64
from threading import Lock
from uuid import uuid1

from celery import shared_task
from django.core.files.base import ContentFile

from .models import FlashcardStyle, Flashcard
from .renderer.renderer import FlashcardRenderer
from .workers import generateImages, generateFlashcard
from ..words.models import Word, WordImage

flashcardCreationLock = Lock()


@shared_task
def createFlashcard(word: int | str, style: int | str, imageIds: list[int]):
    """
    Create a flashcard.

    Generates the word data and images, and then templates and renders a flashcard for
    the word.

    Args:
        Word: The word to generate a flashcard. Either an ID that links to a given word,
            or a string that is the word, in which case the word data will be generated.
        Style: The style of flashcard to generate. Either an ID that links to a given
            flashcard style, or the string key of the desired flashcard style.
        Images: A list of images to use for generating the flashcard. This should be a
            list of IDs of the images to use. If not enough images are passed new ones
            will be generated as-needed.
    """

    # Generate the word if it needs to be generated
    if isinstance(word, int):
        word = Word.objects.get(id=word)
    elif isinstance(word, str):
        word = Word.generated(word)
        word.save()
    else:
        raise TypeError("A valid word id or string is required.")

    # Fetch the style of the flashcard
    if isinstance(style, int):
        style = FlashcardStyle.objects.get(id=style)
    elif isinstance(style, str):
        style = FlashcardStyle.objects.get(key=style)
    else:
        raise TypeError("A valid style id or key is required.")

    # Generate the needed images for the flashcard
    images = list(WordImage.objects.filter(id__in=imageIds))
    imagesToGenerate = style.imgCount() - len(images)
    images.extend(generateImages(word, imagesToGenerate, style.imgConfig))

    # Create the flashcard itself
    flashcard = Flashcard(
        word=word,
        style=style,
    )

    flashcardCreationLock.acquire()
    renderer = FlashcardRenderer(flashcard, images)
    renderedFront = base64.b64decode(renderer.rendered("front"))
    renderedBack = base64.b64decode(renderer.rendered("back"))
    flashcard.front = ContentFile(renderedFront, f"{str(uuid1())}.pdf")
    flashcard.back = ContentFile(renderedBack, f"{str(uuid1())}.pdf")
    flashcardCreationLock.release()

    flashcard.save()
    return generateFlashcard(word, style, images)
