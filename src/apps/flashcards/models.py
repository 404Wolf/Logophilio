import asyncio
import base64
from functools import cache
from typing import Literal

import aiohttp
import jinja2
from django.db import models
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField

from .converter import convertToPdf
from .generator.generator import FlashcardGen
from .generator.graphics import icons
from .validators import validate_style_filetype


class Word(models.Model):
    word = models.CharField(max_length=50, unique=True, primary_key=True)
    partOfSpeech = models.CharField(max_length=20)
    pronunciation = models.CharField(max_length=100)
    offensive = models.BooleanField(default=False)
    synonyms = ArrayField(models.CharField(max_length=50), size=8)
    antonyms = ArrayField(models.CharField(max_length=50), size=8)
    sentences = ArrayField(models.CharField(max_length=400), size=8)
    definitions = ArrayField(models.CharField(max_length=400), size=8)
    inspirationalQuotes = ArrayField(models.CharField(max_length=400), size=8)
    rhymes = ArrayField(models.CharField(max_length=50), size=8)
    notes = models.TextField(null=True)

    @classmethod
    async def generated(cls, word: str):
        word = {}
        async with aiohttp.ClientSession() as session:
            generator = FlashcardGen(word, session)
            with asyncio.TaskGroup() as taskGroup:
                # fmt:off
                word = {
                    "word": word,
                    "partOfSpeech": taskGroup.create_task(generator.partOfSpeech()),
                    "pronunciation": taskGroup.create_task(generator.pronunciation()),
                    "offensive": taskGroup.create_task(generator.partOfSpeech()),
                    "synonyms": taskGroup.create_task(generator.synonyms()),
                    "antonyms": taskGroup.create_task(generator.antonyms()),
                    "sentences": taskGroup.create_task(generator.sentences()),
                    "definitions": taskGroup.create_task(generator.definitions()),
                    "inspirationalQuotes": taskGroup.create_task(generator.inspirationalQuotes()),
                    "rhymes": taskGroup.create_task(generator.rhymes()),
                }
                # fmt:on
                for key, value in word.items():
                    word[key] = await value.result()
        return cls(**word)


class WordImage(models.Model):
    word = models.CharField(max_length=50)
    width = models.IntegerField()
    height = models.IntegerField()
    dalleTemplate = models.TextField()
    notes = models.TextField(null=True)
    image = models.ImageField(null=True)


class FlashcardStyle(models.Model):
    name = models.CharField(max_length=50)
    front = models.FileField(validators=[validate_style_filetype], null=True)
    back = models.FileField(validators=[validate_style_filetype], null=True)
    width = models.IntegerField()
    height = models.IntegerField()
    config = JSONField(default=dict)

    @cache
    def template(self, side: Literal["front", "back"]):
        with open(getattr(self, side), "r") as templateStr:
            templateStr = templateStr.read()
            return jinja2.Environment().from_string(templateStr)


class Flashcard(models.Model):
    front = models.FileField(null=True)
    back = models.FileField(null=True)
    word = models.ForeignKey(Word, on_delete=models.SET_NULL, null=True)
    style = models.ForeignKey(FlashcardStyle, on_delete=models.SET_NULL, null=True)

    def templated(self, template: jinja2.Template, **kwargs) -> str:
        """Slot flashcard data into a SVG template."""
        templateFields = {**kwargs, "WORD_1": self.word.word}
        for fieldName, value in (
            ("WORD", self.word.word),
            ("PART_OF_SPEECH", self.word.partOfSpeech),
            ("PRONUNCIATION", self.word.pronunciation),
            ("OFFENSIVE", self.word.offensive),
            ("SYNONYMS", self.word.synonyms),
            ("ANTONYMS", self.word.antonyms),
            ("SENTENCES", self.word.sentences),
            ("DEFINITIONS", self.word.definitions),
            ("INSPIRATIONAL_QUOTES", self.word.inspirationalQuotes),
            ("RHYMES", self.word.rhymes),
        ):
            if isinstance(value, list):
                for i, item in enumerate(value, start=1):
                    templateFields[f"{fieldName}_{i}"] = str(item)
            else:
                templateFields[f"{fieldName}_1"] = str(value)
        templateFields["PART_OF_SPEECH_ICON_1"] = str(icons[self.word.partOfSpeech])
        return template.render(**templateFields)

    def rendered(
        self,
        template: jinja2.Template,
        additionalTemplatingFields: dict[str, list[str] | str] = None,
    ):
        """Slot flashcard data into a rendered PDF flashcard."""
        templated = self.templated(template)
        templated_b64 = (
            f"data:image/svg+xml;base64,{base64.b64encode(templated.encode('utf-8'))}"
        )
        return convertToPdf(templated_b64, **(additionalTemplatingFields or {}))
