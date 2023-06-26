from flashcards.flashcard import Flashcard
from src.flashcards.renderers.utils import fileAsBase64

flashcard = Flashcard(
    word="propinquity",
    partOfSpeech="noun",
    pronunciation="proh-ping-kwi-tee",
    synonyms=["closeness", "nearness", "proximity", "affinity", "kinship", "likeness"],
    sentences=[
        "The propinquity of the two buildings made it easy to move between them.",
        "Propinquity is a good thing when you are trying to get to know someone.",
        "The propinquity of the two buildings made it easy to move between them.",
    ],
    definitions=[
        "the state of being close to someone or something",
        "nearness in place, time, or blood",
        "similarity in nature",
    ],
    quotes=[
        "Propinquity breeds possibility; the closer we are to something, the more "
        "likely we are to achieve it"
    ],
    rhyming=["proximity", "affinity", "kinship", "likeness", "closeness", "nearness"],
    images=[fileAsBase64("flashcards/graphics/examples/wordImage.png")],
)

with open("output.pdf", "wb") as output_file:
    output_file.write(flashcard.render("watercolor", "mini"))
