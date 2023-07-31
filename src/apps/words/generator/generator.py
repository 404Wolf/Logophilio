import asyncio
import json
import logging
import os
import re
import string
from contextlib import suppress
from copy import copy, deepcopy

from aiohttp import ContentTypeError
from dotenv import load_dotenv

import aiohttp
from unidecode import unidecode

from ..utils import formatting
from ..utils.openai import gptReq

load_dotenv()

logger = logging.getLogger(__name__)

# fmt: off
BASIC_WEBSTER_THESAURUS = "https://www.dictionaryapi.com/api/v3/references/thesaurus/json"
ADVANCED_WEBSTER_THESAURUS = "https://www.dictionaryapi.com/api/v3/references/ithesaurus/json/"
RHYMEZONE_API = "https://api.datamuse.com/words"
RHYMEBRAIN_API = "https://rhymebrain.com/talk?function=getRhymes"
DICTIONARY_API = "https://api.dictionaryapi.dev/api/v2/entries/en"
# fmt: on

with open("apps/words/generator/prompts.json") as f:
    aiPrompts = json.load(f)


class WordDataGenerator:
    """
    A generator for various parts of data about a english word.

    Methods:
        partOfSpeech: The part of speech of the word.
        pronunciation: The pronunciation of the word.
        offensive: Whether the word is offensive or not.
        synonyms: Synonyms of the word.
        antonyms: Antonyms of the word.
        sentences: Sentences of the word.
        definitions: Definitions of the word.
        inspirationalQuotes: Inspirational quotes of the word.
        rhymes: Words that rhyme with the word.
        images: Images of the word.
    """

    def __init__(self, word: str, session: aiohttp.ClientSession):
        self.word = word
        self.session = session

        self._partOfSpeech = None
        self._pronunciation = None
        self._offensive = False
        self._synonyms = []
        self._antonyms = []
        self._sentences = []
        self._definitions = []
        self._inspirationalQuotes = []
        self._rhymes = []
        self._images = []

        self._basic_thesaurus_api_fetched = False
        self._advanced_thesaurus_api_fetched = False
        self._rhyming_api1_fetched = False
        self._rhyming_api2_fetched = False
        self._dictionary_api_fetched = False

    async def partOfSpeech(self):
        """Part of speech of the word"""
        logger.debug("Entering partOfSpeech method.")
        if not self._partOfSpeech:
            logger.info("Part of speech not available. Generating...")
            await self._genPartOfSpeech()
        partOfSpeech = self._partOfSpeech.lower()
        logger.debug("Returning part of speech: %s", partOfSpeech)
        return partOfSpeech

    async def pronunciation(self):
        """Pronunciation of the word."""
        logger.debug("Entering pronunciation method.")
        if not self._pronunciation:
            logger.info("Pronunciation not available. Generating...")
            await self._genPronunciation()
        pronunciation = unidecode(self._pronunciation)
        logger.debug("Original pronunciation: %s", self._pronunciation)
        logger.debug("Normalized pronunciation: %s", pronunciation)
        return pronunciation.lower()

    async def synonyms(self, count: int = 8):
        """Synonyms of the word."""
        logger.debug("Entering synonyms method.")
        if not self._synonyms:
            logger.info(
                "Synonyms not available. Attempting to fetch data from basic thesaurus API."
            )
            if not self._basic_thesaurus_api_fetched:
                await self._fetchBasicThesaurusData()
        if not self._synonyms:
            logger.info(
                "Basic thesaurus API data not available. Attempting to fetch data from advanced thesaurus API."
            )
            if not self._advanced_thesaurus_api_fetched:
                await self._fetchAdvancedThesaurusData()
        if not self._synonyms or len(self._synonyms) < count:
            synonymCount = len(self._synonyms) if self._synonyms is not None else 0
            logger.debug("Generating additional synonyms: %d", count - synonymCount)
            await self._genSynonyms(count - synonymCount)
        synonyms = filter(lambda synonym: "-" not in synonym, self._synonyms)
        synonyms = filter(lambda synonym: len(synonym) < 12, synonyms)
        logger.debug("Returning %d synonyms.", count)
        return list(synonyms)[:count]

    async def antonyms(self, count: int = 8):
        """Antonyms of the word."""
        logger.debug("Entering antonyms method.")
        if not self._antonyms:
            logger.info(
                "Antonyms not available. Attempting to fetch data from basic thesaurus API."
            )
            if not self._basic_thesaurus_api_fetched:
                await self._fetchBasicThesaurusData()
        if not self._antonyms:
            logger.info(
                "Basic thesaurus API data not available. Attempting to fetch data from advanced thesaurus API."
            )
            if not self._advanced_thesaurus_api_fetched:
                await self._fetchAdvancedThesaurusData()
        if not self._antonyms or len(self._antonyms) < count:
            antonymCount = len(self._antonyms) if self._antonyms is not None else 0
            logger.debug("Generating additional antonyms: %d", count - antonymCount)
            await self._genAntonyms(count - antonymCount)

        logger.debug("Returning %d antonyms.", count)
        return self._antonyms[:count]

    async def sentences(
        self,
        count: int = 8,
    ):
        """Sentences using the word."""
        logger.debug("Entering get_sentences method.")
        if not self._sentences:
            logger.info(
                "Sentences not available. Attempting to fetch data from dictionary API."
            )
            await self._fetchDictionaryData()
        while len(self._sentences) < count:
            logger.debug(
                "Generating additional sentences: %d", count - len(self._sentences)
            )
            await self._genSentences(count - len(self._sentences))
        logger.debug("Returning %d sentences.", count)
        return self._sentences[:count]

    async def definitions(self, count: int = 8):
        """Definitions of the word."""
        logger.debug("Entering definitions method.")
        if not self._definitions:
            logger.info(
                "Definitions not available. Attempting to fetch data from dictionary API."
            )
            await self._fetchDictionaryData()
        if len(self._definitions) < count:
            logger.debug(
                "Generating additional definitions: %d", count - len(self._definitions)
            )
            await self._genDefinitions(count - len(self._definitions))
        logger.debug("Returning %d definitions.", count)
        return self._definitions[:count]

    async def inspirationalQuotes(self, count: int = 6):
        """Inspirational quotes that use the word."""
        logger.debug("Entering inspirationalQuotes method.")
        if not self._inspirationalQuotes:
            logger.info("Inspirational quotes not available. Generating...")
            await self._genInspirationalQuotes(count)
        logger.debug("Returning %d inspirational quotes.", count)
        return self._inspirationalQuotes[:count]

    async def rhymes(self, count: int = 6):
        """Words that rhyme with the word."""
        logger.debug("Entering rhymes method.")
        if not self._rhymes:
            logger.info("Rhymes not available. Generating...")
            await self._genRhymes(count)
        else:
            logger.debug("Generating additional rhymes: %d", count - len(self._rhymes))
            await self._genRhymes(count - len(self._rhymes))

        logger.debug("Returning %d rhymes.", count)
        return self._rhymes

    async def offensive(self) -> bool:
        """Whether the word is offensive or not."""
        logger.debug("Checking if the word is offensive.")

        if self._offensive is None:
            logger.info(
                "Offensiveness status not available. Attempting to fetch data from basic thesaurus API."
            )
            await self._fetchBasicThesaurusData()

        if self._offensive is None:
            logger.info(
                "Basic thesaurus API data not available. Attempting to fetch data from advanced thesaurus API."
            )
            await self._fetchAdvancedThesaurusData()

        if self._offensive is None:
            logger.info("Offensiveness status still not available. Generating...")
            await self._genOffensive()
        logger.debug("Returning offensiveness status: %s", self._offensive)
        return self._offensive

    async def _fetchBasicThesaurusData(self):
        """Fetch data from the basic thesaurus API and store it."""
        logger.debug("Fetching data from the basic thesaurus API.")
        await self._fetchThesaurusData(
            BASIC_WEBSTER_THESAURUS, os.getenv("BASIC_WEBSTER_THESAURUS")
        )
        self._basic_thesaurus_api_fetched = True
        logger.debug("Data from the basic thesaurus API fetched successfully.")

    async def _fetchAdvancedThesaurusData(self):
        """Fetch data from the advanced thesaurus API and store it."""
        logger.debug("Fetching data from the advanced thesaurus API.")
        await self._fetchThesaurusData(
            ADVANCED_WEBSTER_THESAURUS, os.getenv("ADVANCED_WEBSTER_THESAURUS")
        )
        self._advanced_thesaurus_api_fetched = True
        logger.debug("Data from the advanced thesaurus API fetched successfully.")

    async def _fetchThesaurusData(self, apiUrl: str, key: str):
        """
        Fetch data from a Webster thesaurus API and store it.

        Args:
            apiUrl: The URL of the thesaurus API.
            key: The API key for the specific thesaurus API.
        """
        logger.debug("Fetching data from the Webster thesaurus API.")
        with suppress(ContentTypeError, TypeError, IndexError):
            async with self.session.get(
                f"{apiUrl}/{self.word}", params={"key": key}
            ) as resp:
                data = await resp.json()
                synonyms = data[0]["meta"]["syns"]
                if len(synonyms) > 0:
                    synonyms = [synonym.lower() for synonym in synonyms[0]]
                antonyms = data[0]["meta"]["ants"]
                if len(antonyms) > 0:
                    antonyms = [antonym.lower() for antonym in antonyms[0]]
                self._synonyms.extend(synonyms)
                self._antonyms.extend(antonyms)
        logger.debug("Data from the Webster thesaurus API fetched successfully.")

    async def _fetchRhymezoneData(self):
        """Fetch rhyming words with RhymeZone API."""
        logger.debug("Fetching rhyming words with RhymeZone API.")
        rhymes = await self._fetchRhymeData(RHYMEZONE_API)["rhymes"]
        self._rhymes.extend(rhymes)
        self._rhymezoneApiFetched = True
        logger.debug("Rhyming words fetched successfully with RhymeZone API.")

    async def _fetchRhymebrainData(self):
        """Fetch rhyming words with Datamuse API."""
        logger.debug("Fetching rhyming words with Datamuse API.")
        rhymes = await self._fetchRhymeData(RHYMEBRAIN_API)["rhymes"]
        self._rhymes.extend(rhymes)
        self._rhymebrainApiFetched = True
        logger.debug("Rhyming words fetched successfully with Datamuse API.")

    async def _fetchRhymeData(self, apiUrl: str):
        """Fetch rhyming words with a rhyming API."""
        logger.debug("Fetching rhyming words with a rhyming API.")
        async with self.session.get(apiUrl) as resp:
            rhymes = [word["word"].lower() for word in await resp.json()]
        self._rhymes.extend(rhymes)
        logger.debug("Rhyming words fetched successfully with the rhyming API.")

    async def _fetchDictionaryData(self):
        """Fetch various facets of word data from a dictionary API."""
        logger.debug("Fetching data from the dictionary API.")
        origin = None
        definitions = []
        sentences = []
        synonyms = []
        antonyms = []
        with suppress(ContentTypeError, IndexError):
            async with self.session.get(f"{DICTIONARY_API}/{self.word}") as resp:
                data = (await resp.json())[0]
                if "origin" in data:
                    origin = data["origin"].lower()
                partOfSpeech = data["meanings"][0]["partOfSpeech"].lower()
                for entry in data["meanings"]:
                    for meaning in entry["definitions"]:
                        definitions.append(meaning["definition"].lower())
                        synonyms.extend(map(lambda item: item.lower(), meaning["synonyms"]))
                        antonyms.extend(map(lambda item: item.lower(), meaning["antonyms"]))
                        if "example" in meaning and len(meaning["example"].split(" ")) < 14:
                            sentences.append(meaning["example"].lower())
                if origin:
                    self._origin = origin
                self._partOfSpeech = partOfSpeech
                self._definitions.extend(definitions)
                self._sentences.extend(sentences)
                self._synonyms.extend(synonyms)
                self._antonyms.extend(antonyms)
                self._dictionary_api_fetched = True
        logger.debug("Data from the dictionary API fetched successfully.")

    async def _genSynonyms(self, count: int):
        """Generate synonyms using GPT."""
        logger.debug("Generating synonyms using GPT.")
        synonyms = await self._genTextField("synonyms", {"count": count})
        synonyms = [synonym.strip() for synonym in synonyms.split("\n")]
        synonyms = filter(lambda synonym: synonym != self.word, synonyms)
        synonyms = map(lambda synonym: synonym.lower(), synonyms)
        self._synonyms.extend(synonyms)
        logger.debug("Synonyms generated successfully.")

    async def _genAntonyms(self, count: int):
        """Generate antonyms using GPT."""
        logger.debug("Generating antonyms using GPT.")
        antonyms = await self._genTextField("antonyms", {"count": count})
        antonyms = [antonym.strip() for antonym in antonyms.split("\n")]
        antonyms = filter(lambda antonym: antonym != self.word, antonyms)
        antonyms = map(lambda antonym: antonym.lower(), antonyms)
        self._antonyms.extend(antonyms)
        logger.debug("Antonyms generated successfully.")

    async def _genRhymes(self, count: int):
        """Generate rhyming words using GPT."""
        logger.debug("Generating rhyming words using GPT.")
        generated = await self._genTextField("rhymes", {"count": count})
        rhymes = []
        for rhyme in generated.split("\n"):
            if len(rhyme) > 4 and rhyme.lower() != self.word.lower():
                rhyme = rhyme.strip()
                rhyme = rhyme.lower()
                rhymes.append(rhyme)
        self._rhymes.extend(rhymes)
        logger.debug("Rhyming words generated successfully.")

    async def _genDefinitions(self, count: int = 1):
        """Generate word definitions using GPT."""
        logger.debug("Generating word definitions using GPT.")
        definitions = await self._genTextField("definitions", {"count": count})
        definitions = [definition.strip()[3:] for definition in definitions.split("\n")]
        self._definitions.extend(definitions)
        logger.debug("Word definitions generated successfully.")

    async def _genSentences(self, count: int = 1):
        """Generate sentence(s) using the word using GPT."""
        logger.debug("Generating sentence(s) using GPT.")
        sentences = (await self._genTextField("sentences", {"count": count}))
        sentences = sentences.split("\n")
        for i, sentence in enumerate(sentences):
            sentences[i] = sentence.strip()
        self._sentences.extend(sentences)
        logger.debug("Sentences generated successfully.")

    async def _genPronunciation(self):
        """Generate word pronunciation using GPT."""
        logger.debug("Generating word pronunciation using GPT.")
        self._pronunciation = await self._genTextField("pronunciation")
        logger.debug("Word pronunciation generated successfully.")

    async def _genPartOfSpeech(self):
        """Generate word part of speech using GPT."""
        logger.debug("Generating word part of speech using GPT.")
        self._partOfSpeech = (await self._genTextField("partOfSpeech")).lower()
        if self._partOfSpeech.endswith("."):
            self._partOfSpeech = self._partOfSpeech[:-1]
        logger.debug("Word part of speech generated successfully.")

    async def _genInspirationalQuotes(self, count: int = 1):
        """Generate inspirational quote(s) using GPT."""
        logger.debug("Generating inspirational quote(s) using GPT.")
        generated = await self._genTextField("inspirationalQuotes", {"count": count})
        quotes = []
        for quote in generated.split("\n"):
            if len(quote) > 14:
                quote = re.search(r"([A-Z][a-z ]+)", quote).group()
                quote = quote + "."
                quotes.append(quote)

        self._inspirationalQuotes.extend(quotes)
        logger.debug("Inspirational quotes generated successfully.")

    async def _genOrigin(self):
        """Generate word origin using GPT."""
        logger.debug("Generating word origin using GPT.")
        self._origin = await self._genTextField("origin")
        logger.debug("Word origin generated successfully.")

    async def _genOffensive(self):
        """Generate whether the word is offensive or not using GPT."""
        logger.debug("Generating whether the word is offensive or not using GPT.")

        offensive = await self._genTextField("offensive")
        offensive = offensive.lower()
        self._offensive = "yes" in offensive
        logger.debug("Offensiveness status generated successfully.")

    async def _genTextField(self, field: str, placeholders: dict = None):
        """
        Generate text data using GPT.

        Args:
            field: The field to generate text data for.
            placeholders: Placeholders to use in the prompt.

        Returns:
            The generated text data.
        """
        logger.debug(f"Generating text data for field: {field}.")

        placeholders = placeholders or {}
        gptReqData = deepcopy(aiPrompts[field])
        for i, message in enumerate(gptReqData["messages"]):
            gptReqData["messages"][i]["content"] = message["content"].format(
                word=self.word,
                **placeholders,
            )
        logger.debug("Text data generated successfully with GPT.")
        return await gptReq(gptReqData, self.session)
