import random

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from adrf.views import APIView as AsyncAPIView
from django.core.exceptions import ObjectDoesNotExist


from ..flashcards.models import Flashcard, Word, FlashcardStyle


class Generate(AsyncAPIView):
    async def get(self, request: Request, word: str = None):
        word = word.title()

        try:
            style = FlashcardStyle.objects.get(key=request.query_params["style"])
        except KeyError or ObjectDoesNotExist:
            style = random.choice(FlashcardStyle.objects.all())

        try:
            word = Word.objects.get(word=word)
        except ObjectDoesNotExist:
            word = await Word.generated(word)

        flashcard = Flashcard(
            word=word,
            style=style,
        )
        flashcard.front = flashcard.rendered(style.template("front"))
        flashcard.front = flashcard.rendered(style.template("back"))
        flashcard.save()

        return Response({flashcard: flashcard})
