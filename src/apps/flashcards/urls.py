from django.urls import path
from rest_framework.generics import RetrieveAPIView, ListAPIView

from . import views
from .models import Flashcard, FlashcardStyle
from .serializers import FlashcardSerializer, FlashcardStyleSerializer

urlpatterns = [
    path("generate", views.Generate.as_view(), name="generate"),
    path("styles", ListAPIView.as_view(queryset=FlashcardStyle.objects.all(), serializer_class=FlashcardStyleSerializer), name="styles"),
    path("listed/<str:word>", views.Listed.as_view(), name="listed"),
    path("flashcard/<int:pk>", RetrieveAPIView.as_view(queryset=Flashcard.objects.all(), serializer_class=FlashcardSerializer), name="retrieve")
]
