from flashcards.flashcard import Flashcard
from src.flashcards.renderer.render import renderFlashcardFront
from src.flashcards.renderer.utils import file_as_base64

flashcard = Flashcard(
    word="propinquity",
    part_of_speech="noun",
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
    images=[file_as_base64("flashcards/graphics/examples/wordImage.png")],
)

renderFlashcardFront(flashcard, "flashcards/graphics/examples/front.pdf")
