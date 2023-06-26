import base64
import io

from pypdf import PdfWriter

from src.flashcards.graphics import icons
from src.flashcards.renderers.converter import convertToPdf
from src.flashcards.renderers.sizes import sizes


class GenericRendererUsageError(NotImplementedError):
    pass


class GenericRenderer:
    STYLE = "generic"

    def __init__(self, flashcard):
        self.flashcard = flashcard

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

    def renderFront(self, size: str) -> bytes:
        """
        Render the front of a flashcard to a base-64 PDF.

        Args:
            size (str, optional): The size of the flashcard. Defaults to "normal".

        Returns:
            str: The base-64 PDF.
        """
        raise GenericRendererUsageError()

    def renderBack(self, size: str) -> bytes:
        """
        Render the back of a flashcard to a base-64 PDF.

        Args:
            size (str, optional): The size of the flashcard. Defaults to "normal".

        Returns:
            str: The base-64 PDF.
        """
        raise GenericRendererUsageError()

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
        return (
            f"data:image/svg+xml;base64,{icons[self.flashcard.fields.partOfSpeech]}"
        )
