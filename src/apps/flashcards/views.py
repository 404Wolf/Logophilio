import random
from base64 import b64decode, b64encode
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from django.core.files.base import ContentFile
from rest_framework.request import Request
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView

from .serializers import FlashcardSerializer
from .workers import generateFlashcard, generateImages
from ..flashcards.models import FlashcardStyle, Flashcard
from ..words.models import Word, WordImage
from ..words.serializers import WordImageSerializer, WordSerializer


class Generate(APIView):
    def get(self, request: Request):
        # fmt: off
        def createFlashcard(wordStr: str, styleName: str):
            style = FlashcardStyle.objects.get(key=styleName)
            word = Word.generated(wordStr)
            word.save()
            images = generateImages(word, style.imgCount(), style.imgConfig)
            for image in images:
                image.save()
            flashcard = generateFlashcard(word, style, images)
            flashcard.save()
            return {
                "word": word.word,
                "flashcard": FlashcardSerializer(flashcard).data,
            }
        # fmt: on

        flashcards = []
        with ThreadPoolExecutor() as executor:
            for flashcardConfig in request.data["flashcards"]:
                flashcards.append(
                    executor.submit(
                        createFlashcard,
                        flashcardConfig["word"],
                        flashcardConfig["style"],
                    )
                )
            for i, flashcardCreator in enumerate(flashcards):
                flashcards[i] = flashcardCreator.result()

        return Response(flashcards)
