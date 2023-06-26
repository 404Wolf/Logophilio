from src.flashcards.renderers import templates
from src.flashcards.renderers.renderer import GenericRenderer


class WatercolorRenderer(GenericRenderer):
    STYLE = "watercolor"

    def __init__(self, flashcard):
        super().__init__(flashcard)

    def renderFront(self, size: str) -> str:
        """
        Render the front of a flashcard to a base-64 PDF.

        Returns:
            str: The base-64 PDF.
        """
        sentences = self._boldedSentences()
        render = templates[f"{self.STYLE}_{size}"].renderFront(
            WORD=self.flashcard.word.title(),
            IMAGE=self.flashcard.fields.images[0],
            PART_OF_SPEECH=self.flashcard.fields.partOfSpeech,
            PART_OF_SPEECH_ICON=self._partOfSpeechIconBase64(),
            PRONUNCIATION=self.flashcard.fields.pronunciation,
            QUOTE=self.flashcard.fields.quotes[0],
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

    def renderBack(self, size: str) -> str:
        """
        Render the back of a flashcard to a base-64 PDF.

        Returns:
            str: The base-64 PDF.
        """
        return self.renderFront("mini")
