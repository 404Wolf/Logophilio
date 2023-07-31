import base64
from functools import cache
from typing import Literal, Iterable
from uuid import uuid1

import jinja2
from django.core.files.base import ContentFile

from .converter import convertToPdf
from .utils import boldWordOccurances, partOfSpeechAbbreviations, startOutUpper
from ..graphics import icons
from ..models import Flashcard
from ...words.models import Word, WordImage, WordImageConfig

SIDES = Literal["front", "back"]


class FlashcardRenderer:
    """
    A class to template and then render flashcards.

    Attributes:
        flashcard: The flashcard that is being rendered and templated.
        images: Images to use for rendering and templating.

    Methods:
        templated: The templated SVG flashcard.
        rendered: The rendered flashcard PDF.
    """

    def __init__(self, flashcard: Flashcard, images: list[WordImage]):
        self.flashcard = flashcard
        self.images = images

    @property
    def word(self):
        return self.flashcard.word

    def _prepareImages(self):
        imageB64s = []
        for image in self.images:
            with image.image.open("rb") as imageData:
                imageB64s.append(base64.b64encode(imageData.read()).decode("ascii"))
        return [f"data:image/png;base64,{imageB64}" for imageB64 in imageB64s]

    def _fetchTemplatingData(self, side: SIDES):
        frontImgCount = self.flashcard.style.imgCount("front")
        images = self._prepareImages()
        if side == "front":
            images = images[:frontImgCount]
        else:
            images = images[frontImgCount:]

        word = self.word.word.title()
        partOfSpeech = partOfSpeechAbbreviations[self.word.partOfSpeech]
        pronunciation = startOutUpper(self.word.pronunciation.lower())
        offensive = str(self.word.offensive).lower()
        synonyms = [synonym.title() for synonym in self.word.synonyms]
        antonyms = [antonym.title() for antonym in self.word.antonyms]
        rhymes = [rhyme.title() for rhyme in self.word.rhymes]
        definitions = map(startOutUpper, self.word.definitions)
        inspirationalQuotes = map(startOutUpper, self.word.inspirationalQuotes)

        def sentences():
            for sentence in self.word.sentences:
                if len(sentence) > 0:
                    sentence = boldWordOccurances(sentence, self.word.word.lower())
                    sentence = startOutUpper(sentence)
                    yield sentence

        return (
            ("WORD", word),
            ("PART_OF_SPEECH", partOfSpeech),
            ("PRONUNCIATION", pronunciation),
            ("OFFENSIVE", offensive),
            ("SYNONYMS", list(synonyms)),
            ("ANTONYMS", list(antonyms)),
            ("SENTENCES", list(sentences())),
            ("DEFINITIONS", list(definitions)),
            ("INSPIRATIONAL_QUOTES", list(inspirationalQuotes)),
            ("RHYMES", list(rhymes)),
            ("IMAGES", list(images)),
        )

    def _getTemplate(self, side: Literal["front", "back"]):
        return self.flashcard.style.template(side)

    def templated(
        self,
        side: SIDES,
    ) -> str:
        """Slot flashcard data into a SVG template."""
        template = self._getTemplate(side)
        templateFields = {"WORD_1": self.word.word}
        for fieldName, value in self._fetchTemplatingData(side):
            if isinstance(value, list):
                for i, item in enumerate(value, start=1):
                    templateFields[f"{fieldName}_{i}"] = str(item)
            else:
                templateFields[f"{fieldName}_1"] = str(value)
        templateFields["PART_OF_SPEECH_ICON_1"] = str(icons[self.word.partOfSpeech])
        return template.render(**templateFields)

    def rendered(
        self,
        side: SIDES,
    ):
        """Slot flashcard data into a rendered PDF flashcard."""
        templated = self.templated(side)
        templated_b64 = base64.b64encode(templated.encode("utf-8")).decode("utf-8")
        return convertToPdf(
            templated_b64,
            "image/svg+xml",
            self.flashcard.style.width,
            self.flashcard.style.height,
        )


