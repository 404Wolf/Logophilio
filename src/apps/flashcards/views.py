import random

from asgiref.sync import sync_to_async, async_to_sync
from rest_framework.request import Request
from rest_framework.response import Response
from adrf.views import APIView as AsyncAPIView
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView

from ..flashcards.models import FlashcardStyle, Flashcard
from ..words.models import Word, WordImage


class Generate(APIView):
    def get(self, request: Request, word: str = None):
        word = word.title()

        try:
            style = FlashcardStyle.objects.get(key=request.data["style"])
        except KeyError or ObjectDoesNotExist:
            style = random.choice(FlashcardStyle.objects.all())

        try:
            word = Word.objects.get(word=word)
        except ObjectDoesNotExist:
            word = async_to_sync(Word.generated)(word)

        images = list(WordImage.objects.filter(word=word))
        while len(images) < 2:
            images.append(
                async_to_sync(WordImage.generated)(word, style.frontImageConfig)
            )

        flashcard = Flashcard(
            word=word,
            style=style,
        )
        flashcard.front = flashcard.rendered(style.template("front"), images)
        flashcard.front = flashcard.rendered(style.template("back"), images)
        flashcard.save()

        return Response({flashcard: flashcard})
