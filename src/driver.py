import asyncio
import json
from dataclasses import asdict
import logging

from flashcards.flashcard import Flashcard


logging.basicConfig(level=logging.DEBUG)

async def main():
    flashcard = Flashcard("Propinquity", "watercolor")
    await flashcard.generate()

    with open("test.json", "w") as f:
        json.dump(asdict(flashcard.fields), f, indent=4)


if __name__ == "__main__":
    asyncio.run(main())
