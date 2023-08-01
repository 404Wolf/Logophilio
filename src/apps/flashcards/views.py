from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import FlashcardSerializer
from .tasks import createFlashcard
from ..flashcards.models import Flashcard
from ..words.models import Word


class Generate(APIView):
    def get(self, request: Request):
        flashcardCreators = []
        for flashcardConfig in request.data["flashcards"]:
            flashcardCreator = createFlashcard.delay(
                style=flashcardConfig["style"],
                word=flashcardConfig["word"],
                imageIds=flashcardConfig.get("images", []),
            )
            flashcardCreators.append(flashcardCreator)
        print("TEST")
        print(flashcardCreators)

        return Response("Test")


class Listed(APIView):
    def get(self, request: Request, word: str):
        flashcards = []
        for word in Word.objects.filter(word=word):
            results = Flashcard.objects.filter(word=word)
            results = map(lambda result: FlashcardSerializer(result).data, results)
            flashcards.extend(results)
        return Response({"flashcards": flashcards})
