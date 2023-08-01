from rest_framework import serializers
from .models import (
    WordImage as WordImageModel,
    Word as WordModel,
)


class LimitedWordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WordModel
        fields = ["id", "word"]


class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordModel
        fields = "__all__"


class WordImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordImageModel
        fields = "__all__"
