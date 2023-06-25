import os
from uuid import uuid1

from src.flashcards.flashcard import Flashcard
from .converter import convert_to_pdf
from .templates.templates import flashcardFrontTemplate
from os import path

from .utils import file_as_base64


def renderFlashcardFront(flashcard: Flashcard, output: str) -> None:
    """
    Render the front of a flashcard.

    Args:
        flashcard (Flashcard): The flashcard to render.
        output (str): The path to the output file on disk.
    """
    temp_filepath = f"flashcards/renderer/temp/{str(uuid1())}.svg"

    part_of_speech_icon = file_as_base64(
        path.join(
            "flashcards",
            "graphics",
            "part_of_speech_icons",
            f"{flashcard.fields.part_of_speech}.svg",
        )
    )
    part_of_speech_icon = f"data:image/svg+xml;base64,{part_of_speech_icon}"

    sentences = []
    for sentence in flashcard.fields.sentences:
        sentence = sentence.lower()
        sentence = sentence.replace(flashcard.word.lower(), f"<b>{flashcard.word}</b>")
        if sentence[0:3] == "<b>":
            sentence = sentence[0:3] + sentence[3].upper() + sentence[4:]
        else:
            sentence = sentence[0].upper() + sentence[1:]
        sentences.append(sentence)

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
        SENTENCE_1=sentences[0],
        SENTENCE_2=sentences[1],
        SENTENCE_3=sentences[2],
    )

    try:
        with open(temp_filepath, "w") as f:
            f.write(front_svg)

        convert_to_pdf(temp_filepath, output)
    finally:
        os.remove(temp_filepath)
