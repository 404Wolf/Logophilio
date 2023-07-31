import base64
from functools import cache
from typing import Literal

import jinja2
from django.db import models

from ..flashcards.renderer.converter import convertToPdf
from .validators import validate_style_filetype


class FlashcardStyle(models.Model):
    # fmt:off
    key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField(null=True)
    front = models.FileField(validators=[validate_style_filetype], null=True)
    back = models.FileField(validators=[validate_style_filetype], null=True)
    width = models.IntegerField()
    height = models.IntegerField()
    imgConfig = models.ForeignKey("words.WordImageConfig", on_delete=models.SET_NULL, null=True, related_name="backImageConfig")
    # fmt:on

    @cache
    def templateStr(self, side: Literal["front", "back"]):
        with getattr(self, side).open(mode="r") as templateStr:
            return templateStr.read()

    @cache
    def template(self, side: Literal["front", "back"]):
        return jinja2.Environment().from_string(self.templateStr(side))

    def imgCount(self, side: Literal["front", "back"] = None):
        if side is None:
            count = 0
            for side in ("front", "back"):
                count += self.templateStr(side).count(r"{{ IMAGES_")
            return count
        return self.templateStr(side).count(r"{{ IMAGES_")


class Flashcard(models.Model):
    front = models.FileField(null=True)
    back = models.FileField(null=True)
    word = models.ForeignKey("words.Word", on_delete=models.SET_NULL, null=True)
    style = models.ForeignKey(FlashcardStyle, on_delete=models.SET_NULL, null=True)
