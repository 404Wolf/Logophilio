import base64
import io

from pypdf import PdfWriter

from src.converter import convertToPdf
from src.flashcards.flashcard import Flashcard
from src.flashcards.graphics import icons
from src.flashcards.renderer import templates
from src.flashcards.renderer.sizes import sizes
from src.flashcards.styles import styles


class GenericRendererUsageError(NotImplementedError):
    pass


class Renderer:
    """
    A renderer for flashcards.

    Fills in a flashcard SVG with the appropriate information, and renders it to a PDF.

    Attributes:
        flashcard: The flashcard to render.
    """

    def __init__(self, flashcard: Flashcard):
        """
        Initialize a GenericRenderer.
        """
        self.flashcard = flashcard

    @property
    def style(self):
        """
        The style of the flashcard.
        """
        return self.flashcard.style

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

    def renderFront(self, size: str) -> str:
        """
        Render the front of a flashcard to a base-64 PDF.

        Args:
            size (str, optional): The size of the flashcard. Defaults to "normal".

        Returns:
            str: The base-64 PDF.
        """
        return self.renderBack(size)

    def renderBack(self, size: str) -> str:
        """
        Render the back of a flashcard to a base-64 PDF.

        Args:
            size (str, optional): The size of the flashcard. Defaults to "normal".

        Returns:
            str: The base-64 PDF.
        """
        sentences = self._boldedSentences()

        # fmt: off
        fields = {}
        for fieldName, fieldCount in styles[self.style].fields:
            fieldName = fieldName.upper()
            if fieldName > 1:
                for i in range(1, fieldCount + 1):
                    fields[f"{fieldName}_{i}"] = getattr(self.flashcard.fields, fieldName)[i]
            else:
                fields[fieldName] = getattr(self.flashcard.fields, fieldName)
        # fmt: on

        render = templates[self.style].renderFront(
            WORD=self.flashcard.word.title(),
            IMAGE=self.flashcard.fields.images[0],
            PART_OF_SPEECH=self.flashcard.fields.partOfSpeech,
            PART_OF_SPEECH_ICON=self._partOfSpeechIconBase64(),
            PRONUNCIATION=self.flashcard.fields.pronunciation,
            INSPIRATIONAL_QUOTE=self.flashcard.fields.inspirationalQuotes[0],
            SYNONYM_1=self.flashcard.fields.synonyms[0],
            SYNONYM_2=self.flashcard.fields.synonyms[1],
            SYNONYM_3=self.flashcard.fields.synonyms[2],
            SYNONYM_4=self.flashcard.fields.synonyms[3],
            SYNONYM_5=self.flashcard.fields.synonyms[4],
            SYNONYM_6=self.flashcard.fields.synonyms[5],
            SENTENCE_1=sentences[0],
            SENTENCE_2=sentences[1],
            SENTENCE_3=sentences[2],
        )

        return self._processRender(render, size)

    def _processRender(self, render: str, size: str) -> str:
        """
        Perform post-processing on a render and convert it to a base-64 PDF.

        Args:
            render (str): The render to process, as an svg string.
            size (str): The size type of the flashcard.

        Returns:
            str: The base-64 PDF.
        """
        return convertToPdf(
            base64.b64encode(render.encode("utf-8")).decode("utf-8"),
            "image/svg+xml",
            *sizes[size].pixel_dimensions,
        )

    def _boldedSentences(self) -> list[str]:
        """
        Surround the word itself in bold tags.

        Returns:
            list[str]: The sentences with the word itself surrounded in bold tags.
        """
        sentences = []
        for sentence in self.flashcard.fields.sentences:
            sentence = sentence.lower()
            sentence = sentence.replace(
                self.flashcard.word.lower(), f"<b>{self.flashcard.word}</b>"
            )
            if sentence[0:3] == "<b>":
                sentence = sentence[0:3] + sentence[3].upper() + sentence[4:]
            else:
                sentence = sentence[0].upper() + sentence[1:]
            sentences.append(sentence)
        return sentences

    def _partOfSpeechIconBase64(self) -> str:
        """
        Get the base-64 encoded part of speech icon.

        Returns:
            str: The base-64 encoded part of speech icon.
        """
        return f"data:image/svg+xml;base64,{icons[self.flashcard.fields.partOfSpeech]}"
