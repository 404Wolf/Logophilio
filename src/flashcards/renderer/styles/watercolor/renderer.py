from src.flashcards.renderer.renderer import GenericRenderer
from src.flashcards.renderer.styles import templates


class WatercolorRenderer(GenericRenderer):
    STYLE = "watercolor"

    def __init__(self, flashcard):
        super().__init__(flashcard)

    def renderFront(self, size: str) -> bytes:
        """
        Render the front of a flashcard to a base-64 PDF.

        Returns:
            str: The base-64 PDF.
        """
        sentences = self._bolded_sentences()
        render = templates[f"{self.STYLE}_{size}"].renderFront(
            WORD=self.flashcard.word.title(),
            IMAGE=self.flashcard.fields.images[0],
            PART_OF_SPEECH=self.flashcard.fields.part_of_speech,
            PART_OF_SPEECH_ICON=self._part_of_speech_icon_base64(),
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
        return self._process_render(render, size)

    def renderBack(self, size: str) -> bytes:
        """
        Render the back of a flashcard to a base-64 PDF.

        Returns:
            str: The base-64 PDF.
        """
        return self.renderFront("mini")
