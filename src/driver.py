import asyncio
import logging

from flashcards.flashcard import Flashcard
from src.flashcards import styles

logging.basicConfig(level=logging.DEBUG)


async def main():
    flashcard = Flashcard("Propinquity", styles["watercolor"])
    await flashcard.generate()

    with open("output.pdf", "wb") as outputFile:
        outputFile.write(flashcard.render())


if __name__ == "__main__":
    asyncio.run(main())
