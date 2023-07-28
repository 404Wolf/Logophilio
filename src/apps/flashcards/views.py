import random
from base64 import b64decode, b64encode

from django.core.files.base import ContentFile
from rest_framework.request import Request
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView

from .serializers import FlashcardSerializer
from ..flashcards.models import FlashcardStyle, Flashcard
from ..words.models import Word, WordImage
from ..words.serializers import WordImageSerializer


class Generate(APIView):
    def get(self, request: Request, word: str = None):
        word = word.title()

        try:
            style = FlashcardStyle.objects.get(key=request.data["style"])
        except KeyError or ObjectDoesNotExist:
            style = random.choice(FlashcardStyle.objects.all())

        try:
            word = Word.objects.get(word=word.lower())
        except ObjectDoesNotExist:
            word = Word.generated(word.lower())
            word.save()

        images = list(WordImage.objects.filter(word=word))
        while len(images) < 2:
            images.append(image := WordImage.generated(word, style.imageConfig))
            image.save()

        flashcard = Flashcard(
            word=word,
            style=style,
        )
        flashcard.front = ContentFile(
            b64decode(flashcard.rendered(style.template("front"), [images[0]])),
            name="front.pdf",
        )
        flashcard.back = ContentFile(
            b64decode(flashcard.rendered(style.template("back"), [images[1]])),
            name="back.pdf",
        )
        flashcard.save()

        return Response(
            {
                "flashcard": FlashcardSerializer(flashcard).data,
                "images": [WordImageSerializer(image).data for image in images],
            }
        )
