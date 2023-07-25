import asyncio
import base64
import io
import json
from contextlib import asynccontextmanager
from typing import Iterable

import aiohttp
import jinja2
from pypdf import PdfWriter

from src.converter import convertToPdf
from src.flashcards.generator import Generator
from src.flashcards.graphics import icons
from src.flashcards.styles.styles import Style
from src.flashcards.utils.formatting import camelCaseToSnakeCase
from src.flashcards.utils.misc import strAsBase64

fields = (
    "partOfSpeech",
    "pronunciation",
    "offensive",
    "synonyms",
    "antonyms",
    "sentences",
    "definitions",
    "inspirationalQuotes",
    "rhymes",
    "images",
)


class Flashcard:
    def __init__(self, word: str, style: Style):
        """
        A flashcard.

        Args:
            word: The word.
            style: The style of the flashcard.
            fields: The fields of the flashcard.
        """
        self.style = style
        self.fields = dict.fromkeys(fields)
        self._word = word

    @property
    def word(self) -> str:
        return self._word

    def render(self, *args, **kwargs) -> bytes:
        """
        Render a flashcard to a PDF, and return the PDF as a bytes stream.

        Calls renderFront and renderBack, and combines the results into a single PDF.

        Args:
            *args: Positional arguments to pass to renderFront and renderBack.
            **kwargs: Keyword arguments to pass to renderFront and renderBack.

        Returns:
            bytes: The PDF as a bytes stream.
        """
        front = base64.b64decode(self.renderFront(*args, **kwargs))
        back = base64.b64decode(self.renderBack(*args, **kwargs))

        writer = PdfWriter()
        writer.append(io.BytesIO(front))
        writer.append(io.BytesIO(back))

        bytes_stream = io.BytesIO()
        writer.write(bytes_stream)
        bytes_stream.seek(0)
        return bytes_stream.read()

    def renderFront(self, **kwargs) -> str:
        """Render the front of the flashcard to a base-64 PDF."""
        return convertToPdf(
            strAsBase64(self._prerenderFront(**kwargs)), "image/svg+xml", *self.style.size,
        )

    def renderBack(self, **kwargs) -> str:
        """Render the back of the flashcard to a base-64 PDF."""
        return convertToPdf(
            strAsBase64(self._prerenderBack(**kwargs)), "image/svg+xml", *self.style.size,
        )

    def _prerenderBack(self, **kwargs) -> str:
        """Render the back of the flashcard to a templated SVG."""
        return self._prerender(self.style.back, **kwargs)

    def _prerenderFront(self, **kwargs) -> str:
        """Render the front of the flashcard to a templated SVG."""
        return self._prerender(self.style.front, **kwargs)

    def _prerender(self, template: jinja2.Template, **kwargs) -> str:
        """Render a side of the flashcard to a templated SVG."""
        templateFields = {**kwargs, "WORD_1": self.word}
        for fieldName, value in self.fields.items():
            fieldName = camelCaseToSnakeCase(fieldName).upper()
            if isinstance(value, list):
                for i, item in enumerate(value, start=1):
                    templateFields[f"{fieldName}_{i}"] = str(item)
            else:
                templateFields[f"{fieldName}_1"] = str(value)
        templateFields["PART_OF_SPEECH_ICON_1"] = str(icons[self.fields["partOfSpeech"]])
        return template.render(**templateFields)

    @asynccontextmanager
    async def generator(self) -> Generator:
        async with aiohttp.ClientSession() as session:
            yield Generator(self.word, session)

    async def _generate(
        self,
        genFields: list[str] | None = None,
        genKwargs: dict[str, dict[str, object]] | None = None,
    ) -> None:
        """
        Generate the flashcard.

        Args:
            genFields: The fields to generate data for the flashcard. All fields are
                generated if this is None.
            genKwargs: Extra keyword arguments to pass to the respective generator and
                fetchers for given fields. No extra keyword arguments are passed if this
                is None.

        Notes:
            This method clears the current fields of the flashcard.
        """
        genFields = genFields or fields
        genKwargs = dict.fromkeys(fields, {}) | (genKwargs or {})

        async with self.generator() as generator:
            # fmt: off
            tasks = []
            async with asyncio.TaskGroup() as taskGroup:
                for field in genFields:
                    async def fieldGen(_field=field):
                        self.fields[_field] = await getattr(generator, _field)(
                            **genKwargs[_field],
                        )
                    tasks.append(taskGroup.create_task(fieldGen()))
            # fmt: on

    async def generate(self):
        """
        Generate all the needed fields for the flashcard.

        Notes:
            * This method clears the current fields of the flashcard.
            * This method utilizes the styles' configuration for generation.
        """
        await self._generate(
            genKwargs=self.style.config,
        )
