from asgiref.sync import sync_to_async
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Word
from .serializers import WordSerializer


class Generate(APIView):
    def get(self, request: Request, word: str):
        word = Word.generated(word)
        word.save()
        return Response(WordSerializer(word).data)
