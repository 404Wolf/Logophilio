from asgiref.sync import sync_to_async
from rest_framework.generics import RetrieveAPIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Word
from .serializers import WordSerializer


class Generate(APIView):
    def get(self, request: Request):
        words = []
        for word in request.data["words"]:
            word = Word.generated(word["word"])
            word.save()
            words.append(word)
        words = [WordSerializer(word).data for word in words]
        return Response({"words": words})


class Listed(APIView):
    def get(self, request: Request, word: str):
        words = Word.objects.filter(word=word)
        words = [word.pk for word in words]
        return Response({"words": words})


class Retrieve(RetrieveAPIView):
    queryset=Word.objects.all()
    serializer_class = WordSerializer
