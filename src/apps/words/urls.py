from django.urls import path
from rest_framework.generics import ListAPIView, RetrieveAPIView

from . import views
from .models import Word
from .serializers import WordSerializer, LimitedWordSerializer

urlpatterns = [
    path("", ListAPIView.as_view(queryset=Word.objects.all(), serializer_class=LimitedWordSerializer), name="words"),
    path("generate", views.Generate.as_view(), name="generate"),
    path("listed/<str:word>", views.Listed.as_view(), name="listed"),
    path("word/<int:pk>", RetrieveAPIView.as_view(queryset=Word.objects.all(), serializer_class=WordSerializer), name="retrieve")
]
