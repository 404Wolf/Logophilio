from src.flashcards.flashcard import Flashcard
from .templates.templates import flashcardFrontTemplate
from os import path

from .utils import file_as_base64


def renderFlashcardFront(flashcard: Flashcard):
    part_of_speech_icon = file_as_base64(
        path.join(
            "flashcards",
            "graphics",
            "part_of_speech_icons",
            f"{flashcard.fields.part_of_speech}.svg",
        )
    )
    part_of_speech_icon = f"data:image/svg+xml;base64,{part_of_speech_icon}"

    front_svg = flashcardFrontTemplate.render(
        WORD=flashcard.word,
        IMAGE=flashcard.fields.images[0],
        PART_OF_SPEECH=flashcard.fields.part_of_speech,
        PART_OF_SPEECH_ICON=part_of_speech_icon,
        PRONUNCIATION=flashcard.fields.pronunciation,
        QUOTE=flashcard.fields.quotes[0],
        SYNONYM_1=flashcard.fields.synonyms[0],
        SYNONYM_2=flashcard.fields.synonyms[1],
        SYNONYM_3=flashcard.fields.synonyms[2],
        SYNONYM_4=flashcard.fields.synonyms[3],
        SYNONYM_5=flashcard.fields.synonyms[4],
        SYNONYM_6=flashcard.fields.synonyms[5],
        SENTENCE_1=flashcard.fields.sentences[0],
        SENTENCE_2=flashcard.fields.sentences[1],
        SENTENCE_3=flashcard.fields.sentences[2],
    )
    return front_svg
