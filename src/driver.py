import asyncio
import json
import logging
from dataclasses import asdict
from pprint import pprint

from flashcards.flashcard import Flashcard
from src.flashcards import styles

logging.basicConfig(level=logging.DEBUG)


async def main():
    flashcard = Flashcard("Propinquity", styles["watercolor"])
    await flashcard.generate(
        genKwargs={
            "images": {"count": 1},
            "definitions": {"count": 3},
        }
    )
    pprint(flashcard.fields)


if __name__ == "__main__":
    asyncio.run(main())
