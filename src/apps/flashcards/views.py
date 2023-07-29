from copy import copy

from rest_framework.request import Request
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView

from .serializers import FlashcardSerializer
from .workers import generateFlashcard, generateImages
from ..flashcards.models import FlashcardStyle, Flashcard
from ..words.models import Word


class Generate(APIView):
    def get(self, request: Request):
        flashcards = []

        def _createFlashcard(wordStr: str, styleName: str):
            # Fetch the style of flashcard
            if isinstance(styleName, int):
                style = FlashcardStyle.objects.get(id=styleName)
            elif isinstance(styleName, str):
                style = FlashcardStyle.objects.get(key=styleName)

            # Generate metadata for the vocab word that is having a flashcard generated
            try:
                word = Word.objects.get(word=wordStr)
            except ObjectDoesNotExist:
                word = Word.generated(wordStr)
                word.save()

            # Generate the needed images for the flashcard and then save them to the db
            images = generateImages(word, style.imgCount(), style.imgConfig)

            # Generate the flashcard
            flashcard = generateFlashcard(word, style, images)

            # Serialize the flashcard, store the json, and close the db connection
            serialized_flashcard = {
                "word": word.word,
                "flashcard": FlashcardSerializer(flashcard).data,
            }
            flashcards.append(serialized_flashcard)

        for flashcardConfig in request.data["flashcards"]:
            _createFlashcard(flashcardConfig["word"], flashcardConfig["style"])

        return Response({"flashcards": flashcards})


class Listed(APIView):
    def get(self, request: Request, word: str):
        flashcards = []
        for word in Word.objects.filter(word=word):
            results = Flashcard.objects.filter(word=word)
            results = map(lambda result: FlashcardSerializer(result).data, results)
            flashcards.extend(results)
        return Response({"flashcards": flashcards})
