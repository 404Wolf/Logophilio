import asyncio
from contextlib import asynccontextmanager

import aiohttp

from src.flashcards.generator import Generator
from src.flashcards.styles.styles import Style

fields = (
    "partOfSpeech",
    "pronunciation",
    "offensive",
    "synonyms",
    "antonyms",
    "sentences",
    "definitions",
    "inspirationalQuotes",
    "rhymes",
    "images",
)


class Flashcard:
    def __init__(self, word: str, style: Style):
        """
        A flashcard.

        Args:
            word: The word.
            style: The style of the flashcard.
            fields: The fields of the flashcard.
        """
        self.style = style
        self.fields = dict.fromkeys(fields)
        self._word = word

    @property
    def word(self) -> str:
        return self._word

    @asynccontextmanager
    async def generator(self) -> Generator:
        async with aiohttp.ClientSession() as session:
            yield Generator(self.word, session)

    async def generate(
        self,
        genFields: list[str] | None = None,
        genKwargs: dict[str, dict[str, object]] | None = None,
    ) -> None:
        """
        Generate the flashcard.

        Args:
            genFields: The fields to generate data for the flashcard. All fields are
                generated if this is None.
            genKwargs: Extra keyword arguments to pass to the respective generator and
                fetchers for given fields. No extra keyword arguments are passed if this
                is None.

        Notes:
            This method clears the current fields of the flashcard.
        """
        genFields = genFields or fields
        genKwargs = dict.fromkeys(fields, {}) | (genKwargs or {})

        async with self.generator() as generator:
            # fmt: off
            tasks = []
            async with asyncio.TaskGroup() as taskGroup:
                for field in genFields:
                    async def fieldGen(_field=field):
                        self.fields[_field] = await getattr(generator, _field)(
                            **genKwargs[_field],
                        )
                    tasks.append(taskGroup.create_task(fieldGen()))
            # fmt: on
