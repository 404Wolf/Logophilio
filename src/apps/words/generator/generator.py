import asyncio
import json
import os
from dotenv import load_dotenv

import aiohttp
from unidecode import unidecode

from ..utils import formatting
from ..utils.openai import gptReq

load_dotenv()

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
        if not self._partOfSpeech:
            await self._genPartOfSpeech()
        partOfSpeech = self._partOfSpeech.lower()
        return partOfSpeech

    async def pronunciation(self):
        """Pronunciation of the word."""
        if not self._pronunciation:
            await self._genPronunciation()

        pronunciation = unidecode(self._pronunciation)
        return pronunciation.lower()

    async def synonyms(self, count: int = 8):
        """Synonyms of the word."""
        if not self._synonyms:
            if not self._basic_thesaurus_api_fetched:
                await self._fetchBasicThesaurusData()
        if not self._synonyms:
            if not self._advanced_thesaurus_api_fetched:
                await self._fetchAdvancedThesaurusData()
        if not self._synonyms or len(self._synonyms) < count:
            synonymCount = len(self._synonyms) if self._synonyms is not None else 0
            await self._genSynonyms(count - synonymCount)
        synonyms = filter(lambda synonym: "-" not in synonym, self._synonyms)
        return list(synonyms)[:count]

    async def antonyms(self, count: int = 8):
        """Antonyms of the word."""
        if not self._antonyms:
            if not self._basic_thesaurus_api_fetched:
                await self._fetchBasicThesaurusData()
        if not self._antonyms:
            if not self._advanced_thesaurus_api_fetched:
                await self._fetchAdvancedThesaurusData()
        if not self._antonyms or len(self._antonyms) < count:
            await self._genAntonyms(count - len(self._antonyms))
        return self._antonyms[:count]

    async def sentences(
        self,
        count: int = 8,
    ):
        """Sentences using the word."""
        if not self._sentences:
            await self._fetchDictionaryData()
        sentences = self._sentences
        while len(sentences) < count:
            await self._genSentences(count - len(self._sentences))
            sentences = filter(lambda sentence: len(sentence) > 10, self._sentences)
            sentences = list(sentences)
        for i, sentence in enumerate(sentences):
            if not sentence.endswith("."):
                sentence += "."
            sentence = sentence[0].upper() + sentence[1:]
            sentences[i] = sentence
        self._sentences = sentences
        return sentences[:count]

    async def definitions(self, count: int = 8):
        """Definitions of the word."""
        if not self._definitions:
            await self._fetchDictionaryData()
        if len(self._definitions) < count:
            await self._genDefinitions(count - len(self._definitions))
        return self._definitions[:count]

    async def inspirationalQuotes(self, count: int = 6):
        """Inspirational quotes that use the word."""
        if not self._inspirationalQuotes:
            await self._genInspirationalQuotes(count)
        return self._inspirationalQuotes[:count]

    async def rhymes(self, count: int = 6):
        """Words that rhyme with the word."""
        if not self._rhymes:
            await self._genRhymes(count)
        else:
            self._rhymes.extend(await self._genRhymes(count - len(self._rhymes)))
        return self._rhymes

    async def offensive(self) -> bool:
        """Whether the word is offensive or not."""
        if self._offensive is None:
            await self._fetchBasicThesaurusData()
        if self._offensive is None:
            await self._fetchAdvancedThesaurusData()
        if self._offensive is None:
            await self._genOffensive()
        return self._offensive

    async def _fetchBasicThesaurusData(self):
        """Fetch data from the basic thesaurus API and store it."""
        fetchedData = await self._fetchThesaurusData(
            BASIC_WEBSTER_THESAURUS, os.getenv("BASIC_WEBSTER_THESAURUS")
        )
        self._basic_thesaurus_api_fetched = True
        return fetchedData

    async def _fetchAdvancedThesaurusData(self):
        """Fetch data from the advanced thesaurus API and store it."""
        fetchedData = await self._fetchThesaurusData(
            ADVANCED_WEBSTER_THESAURUS, os.getEnv("ADVANCED_WEBSTER_THESAURUS")
        )
        self._advanced_thesaurus_api_fetched = True
        return fetchedData

    async def _fetchThesaurusData(self, apiUrl: str, key: str):
        """
        Fetch data from a Webster thesaurus API and store it.

        Args:
            apiUrl: The URL of the thesaurus API.
            key: The API key for the specific thesaurus API.
        """
        async with self.session.get(
            f"{apiUrl}/{self.word}", params={"key": key}
        ) as resp:
            data = await resp.json()
            synonyms = [synonym.lower() for synonym in data[0]["meta"]["syns"][0]]
            antonyms = [antonym.lower() for antonym in data[0]["meta"]["ants"][0]]
            self._synonyms.extend(synonyms)
            self._antonyms.extend(antonyms)
        return {"synonyms": synonyms, "antonyms": antonyms}

    async def _fetchRhymezoneData(self):
        """Fetch rhyming words with RhymeZone API."""
        rhymes = await self._fetchRhymeData(RHYMEZONE_API)["rhymes"]
        self._rhymezoneApiFetched = True
        return {"rhymes": rhymes}

    async def _fetchRhymebrainData(self):
        """Fetch rhyming words with Datamuse API."""
        rhymes = await self._fetchRhymeData(RHYMEBRAIN_API)["rhymes"]
        self._rhymebrainApiFetched = True
        return {"rhymes": rhymes}

    async def _fetchRhymeData(self, apiUrl: str):
        """Fetch rhyming words with a rhyming API."""
        async with self.session.get(apiUrl) as resp:
            rhymes = [word["word"].lower() for word in await resp.json()]
        self._rhymes.extend(rhymes)
        return {"rhymes": rhymes}

    async def _fetchDictionaryData(self):
        """Fetch various facets of word data from a dictionary API."""
        origin = None
        definitions = []
        sentences = []
        synonyms = []
        antonyms = []
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

        return {
            "origin": origin,
            "partOfSpeech": partOfSpeech,
            "definitions": definitions,
            "sentences": sentences,
            "synonyms": synonyms,
            "antonyms": antonyms,
        }

    async def _genSynonyms(self, count: int):
        """Generate synonyms using GPT."""
        synonyms = await self._genTextField("synonyms", {"count": count})
        synonyms = [synonym.strip() for synonym in synonyms.split("\n")]
        synonyms = filter(lambda synonym: synonym != self.word, synonyms)
        synonyms = map(lambda synonym: synonym.lower(), synonyms)
        self._synonyms.extend(synonyms)
        return {"synonyms": synonyms}

    async def _genAntonyms(self, count: int):
        """Generate antonyms using GPT."""
        antonyms = await self._genTextField("antonyms", {"count": count})
        antonyms = [antonym.strip() for antonym in antonyms.split("\n")]
        antonyms = filter(lambda antonym: antonym != self.word, antonyms)
        antonyms = map(lambda antonym: antonym.lower(), antonyms)
        self._antonyms.extend(antonyms)
        return {"antonyms": antonyms}

    async def _genRhymes(self, count: int):
        """Generate rhyming words using GPT."""
        rhymes = await self._genTextField("rhymes", {"count": count})
        rhymes = [rhyme.strip() for rhyme in rhymes.split("\n")]
        rhymes = filter(lambda rhyme: rhyme != self.word, rhymes)
        rhymes = map(lambda rhyme: rhyme.lower(), rhymes)
        self._rhymes.extend(rhymes)
        return {"rhymes": rhymes}

    async def _genDefinitions(self, count: int = 1):
        """Generate word definitions using GPT."""
        definitions = await self._genTextField("definitions", {"count": count})
        definitions = [definition.strip()[3:] for definition in definitions.split("\n")]
        self._definitions.extend(definitions)
        return {"definitions": definitions}

    async def _genSentences(self, count: int = 1):
        """Generate sentence(s) using the word using GPT."""
        sentences = await self._genTextField("sentences", {"count": count})
        sentences = [sentence.strip() for sentence in sentences.split("\n")]
        self._sentences.extend(sentences)
        return {"sentences": sentences}

    async def _genPronunciation(self):
        """Generate word pronunciation using GPT."""
        self._pronunciation = await self._genTextField("pronunciation")
        return {"pronunciation": self._pronunciation}

    async def _genPartOfSpeech(self):
        """Generate word part of speech using GPT."""
        self._partOfSpeech = (await self._genTextField("partOfSpeech")).lower()
        return {"partOfSpeech": self._partOfSpeech}

    async def _genInspirationalQuotes(self, count: int = 1):
        """Generate inspirational quote(s) using GPT."""
        quotes = await self._genTextField("inspirationalQuotes", {"count": count})
        quotes = quotes.split("\n")
        for i, quote in enumerate(quotes):
            quote = quote.strip()[4:-1].replace(". \"", "")
            if not quote.endswith("."):
                quote += "."
            quotes[i] = quote
        quotes = filter(lambda quote: len(quote) > 15, quotes)
        self._inspirationalQuotes.extend(quotes)
        return {"inspirationalQuotes": quotes}

    async def _genOrigin(self):
        """Generate word origin using GPT."""
        self._origin = await self._genTextField("origin")
        return {"origin": self._origin}

    async def _genOffensive(self):
        """Generate whether the word is offensive or not using GPT."""
        offensive = await self._genTextField("offensive")
        offensive = offensive.lower()
        self._offensive = "yes" in offensive
        return {"offensive": self._offensive}

    async def _genTextField(self, field: str, placeholders: dict = None):
        """
        Generate text data using GPT.

        Args:
            field: The field to generate text data for.
            placeholders: Placeholders to use in the prompt.

        Returns:
            The generated text data.
        """
        placeholders = placeholders or {}
        gptReqData = aiPrompts[field]
        for i, message in enumerate(gptReqData["messages"]):
            gptReqData["messages"][i]["content"] = message["content"].format(
                word=self.word,
                **placeholders,
            )
        return await gptReq(gptReqData, self.session)
