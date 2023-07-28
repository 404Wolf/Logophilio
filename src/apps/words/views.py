from asgiref.sync import sync_to_async
from rest_framework.request import Request
from rest_framework.response import Response
from adrf.views import APIView as AsyncAPIView

from .models import Word
from .serializers import WordSerializer


class Generate(AsyncAPIView):
    async def get(self, request: Request, word: str):
        word = await Word.generated(word)
        await sync_to_async(word.save)()
        return Response(WordSerializer(word).data)
