from rest_framework import serializers

from src.apps.flashcards.models import (
    FlashcardStyle as FlashcardStyleModel,
    Flashcard as FlashcardModel,
    Word as WordModel,
    WordImage as WordImageModel,
)


class FlashcardStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashcardStyleModel


class FlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashcardModel


class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordModel


class WordImageSerializer(serializers.Serializer):
    class Meta:
        model = WordImageModel
