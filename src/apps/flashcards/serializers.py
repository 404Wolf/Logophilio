from rest_framework import serializers

from .models import (
    FlashcardStyle as FlashcardStyleModel,
    Flashcard as FlashcardModel
)


class FlashcardStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashcardStyleModel
        fields = '__all__'


class FlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashcardModel
        fields = '__all__'

