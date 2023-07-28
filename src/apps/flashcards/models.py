import base64
from functools import cache
from typing import Literal

import jinja2
from django.db import models
from django.db.models import JSONField

from .converter import convertToPdf
from .validators import validate_style_filetype
from ..flashcards.graphics import icons
from ..words.models import WordImage


class FlashcardStyle(models.Model):
    # fmt:off
    key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True)
    front = models.FileField(validators=[validate_style_filetype], null=True)
    back = models.FileField(validators=[validate_style_filetype], null=True)
    width = models.IntegerField()
    height = models.IntegerField()
    frontImageConfig = models.ForeignKey("words.WordImageConfig", on_delete=models.SET_NULL, null=True, related_name="frontImageConfig")
    backImageConfig = models.ForeignKey("words.WordImageConfig", on_delete=models.SET_NULL, null=True, related_name="backImageConfig")
    # fmt:on

    @cache
    def template(self, side: Literal["front", "back"]):
        with getattr(self, side).open(mode="r") as templateStr:
            templateStr = templateStr.read()
            return jinja2.Environment().from_string(templateStr)


class Flashcard(models.Model):
    front = models.FileField(null=True)
    back = models.FileField(null=True)
    word = models.ForeignKey("words.Word", on_delete=models.SET_NULL, null=True)
    style = models.ForeignKey(FlashcardStyle, on_delete=models.SET_NULL, null=True)

    def templated(
        self,
        template: jinja2.Template,
        images: list[WordImage],
        **kwargs,
    ) -> str:
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
            ("IMAGES", images),
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
        images: list[WordImage],
        additionalTemplatingFields: dict[str, list[str] | str] = None,
    ):
        """Slot flashcard data into a rendered PDF flashcard."""
        additionalTemplatingFields = additionalTemplatingFields or {}
        templated = self.templated(template, images, **additionalTemplatingFields)
        templated_b64 = base64.b64encode(templated.encode("utf-8")).decode("utf-8")
        return convertToPdf(
            templated_b64, "image/svg+xml", self.style.width, self.style.height
        )
