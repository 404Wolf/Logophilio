from rest_framework import serializers
from .models import (
    WordImage as WordImageModel,
    Word as WordModel,
)


class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordModel
        fields = '__all__'


class WordImageSerializer(serializers.Serializer):
    class Meta:
        model = WordImageModel
        fields = '__all__'
