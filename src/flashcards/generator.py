import asyncio
import json
import string

import aiohttp

from src import keys
from src.flashcards.utils import formatting
from src.flashcards.utils.openai import gptReq, dalleReq
from src.flashcards.utils.structs import Image

# fmt: off
BASIC_WEBSTER_THESAURUS = "https://www.dictionaryapi.com/api/v3/references/thesaurus/json"
ADVANCED_WEBSTER_THESAURUS = "https://www.dictionaryapi.com/api/v3/references/ithesaurus/json/"
RHYMEZONE_API = "https://api.datamuse.com/words"
RHYMEBRAIN_API = "https://rhymebrain.com/talk?function=getRhymes"
DICTIONARY_API = "https://api.dictionaryapi.dev/api/v2/entries/en"
# fmt: on

with open("flashcards/prompts.json") as f:
    aiPrompts = json.load(f)


class Generator:
    """
    A generator for flashcard fields.

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

    async def partOfSpeech(self, abbreviate: bool = False):
        """
        The part of speech of the word

        Args:
            abbreviate: Whether to abbreviate the part of speech of the word.

        Returns:
            The part of speech of the    word
        """
        if not self._partOfSpeech:
            await self._genPartOfSpeech()
        partOfSpeech = self._partOfSpeech.lower()
        if abbreviate:
            return {
                "noun": "noun",
                "verb": "verb",
                "adjective": "adj",
                "adverb": "adv",
                "pronoun": "pron",
                "preposition": "prep",
                "conjunction": "conj",
                "interjection": "interj",
                "abbreviation": "abbr",
            }[partOfSpeech]
        else:
            return partOfSpeech

    async def pronunciation(self, lowercase: bool = False):
        """
        The pronunciation of the word.

        Args:
            lowercase: Whether to lowercase the pronunciation of the word. This will
                remove capitalization meant to indicate emphasis.

        Returns:
            The pronunciation of the word.
        """
        if not self._pronunciation:
            await self._genPronunciation()
        if lowercase:
            return self._pronunciation.lower()
        else:
            return self._pronunciation

    async def synonyms(self, count: int = 1):
        """
        Synonyms of the word.

        Args:
            count: The minimum number of synonyms to return.

        Returns:
            Synonyms of the word.
        """
        if not self._synonyms:
            if not self._basic_thesaurus_api_fetched:
                await self._fetchBasicThesaurusData()
        if not self._synonyms:
            if not self._advanced_thesaurus_api_fetched:
                await self._fetchAdvancedThesaurusData()
        if not self._synonyms or len(self._synonyms) < count:
            synonymCount = len(self._synonyms) if self._synonyms is not None else 0
            await self._genSynonyms(count - synonymCount)
        return self._synonyms

    async def antonyms(self, count: int = 1):
        """
        Antonyms of the word.

        Args:
            count: The number of antonyms to return.

        Returns:
            Antonyms of the word.
        """
        if not self._antonyms:
            if not self._basic_thesaurus_api_fetched:
                await self._fetchBasicThesaurusData()
        if not self._antonyms:
            if not self._advanced_thesaurus_api_fetched:
                await self._fetchAdvancedThesaurusData()
        if not self._antonyms or len(self._antonyms) < count:
            await self._genAntonyms(count - len(self._antonyms))
        return self._antonyms

    async def sentences(
        self,
        count: int = 1,
        boldTag: bool = False,
        punctuate: bool = False,
    ):
        """
        Sentences using the word.

        Args:
            count: The number of sentences to return.
            boldTag: Whether to bold the word in the sentences.
            punctuate: Whether to punctuate the sentences.

        Returns:
            Sentences using the word.
        """
        if not self._sentences:
            await self._fetchDictionaryData()
        if not self._sentences or len(self._sentences) < count:
            await self._genSentences(count - len(self._sentences))
        sentences = self._sentences[:count]

        if boldTag:
            sentences = map(formatting.embolden, sentences)

        if punctuate:
            sentences = map(formatting.punctuate, sentences)
        else:
            sentences = map(formatting.depunctuate, sentences)

        return tuple(sentences)

    async def definitions(
        self,
        count: int = 1,
        punctuate: bool = False,
        capitaize: bool = False,
    ):
        """
        Definitions of the word.

        Args:
            count: The number of definitions to return.
            punctuate: Whether to punctuate the definitions.
            capitaize: Whether to capitalize the definitions.
        """
        if not self._definitions:
            await self._fetchDictionaryData()
        if len(self._definitions) < count:
            await self._genDefinitions(count - len(self._definitions))
        definitions = self._definitions[:count]

        if punctuate:
            definitions = map(formatting.punctuate, definitions)
        else:
            definitions = map(formatting.depunctuate, definitions)

        if capitaize:
            definitions = map(formatting.capitalize, definitions)

        return tuple(definitions)

    async def inspirationalQuotes(self, count: int = 1):
        """
        Inspirational quotes that use the word.

        Args:
            count: The number of inspirational quotes to return.
        """
        if not self._inspirationalQuotes:
            await self._genInspirationalQuotes(count)
        return self._inspirationalQuotes

    async def rhymes(self, count: int = 1):
        """
        Words that rhyme with the word.

        Args:
            count: The number of rhymes to return.
        """
        if not self._rhymes:
            await self._genRhymes(count)
        else:
            self._rhymes.extend(await self._genRhymes(count - len(self._rhymes)))
        return self._rhymes

    async def images(self, count: int = 1, dalleTemplate=None):
        """
        Images that relate to the word.

        Args:
            count: The number of images to return.
            dalleTemplate: The template to use for DALL-E images. If None, the prompt
                will be generated automatically and used alone. If a string with a
                single {prompt} placeholder, the prompt will be generated automatically
                generated and slotted into the template.
        """
        if not self._images:
            await self._genImages(count, dalleTemplate=dalleTemplate)
        if len(self._images) < count:
            await self._genImages(count - len(self._images), dalleTemplate=dalleTemplate)
        return self._images[:count]

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
            BASIC_WEBSTER_THESAURUS, keys.BASIC_WEBSTER_THESAURUS
        )
        self._basic_thesaurus_api_fetched = True
        return fetchedData

    async def _fetchAdvancedThesaurusData(self):
        """Fetch data from the advanced thesaurus API and store it."""
        fetchedData = await self._fetchThesaurusData(
            ADVANCED_WEBSTER_THESAURUS, keys.ADVANCED_WEBSTER_THESAURUS
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
                    if "example" in meaning:
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
        rhymes = await self._genTextField("rhyming", {"count": count})
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
        quotes = [quote.strip() for quote in quotes.split("\n")]
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

    async def _genImages(self, count: int = 1, dalleTemplate: str = None) -> list[str]:
        """
        Generate images representing the word with DALLE.

        Args:
            count: The number of images to generate.
            dalleTemplate: The template to use for generating images. If None, the
                prompt itself will be used as the template. The template should
                contain the word to generate images for as {word}.
        """
        imagePrompts = await self._genTextField("dallePrompt", {"count": count})
        imagePrompts = [
            formatting.depunctuate(prompt.strip()[3:])
            for prompt in imagePrompts.split("\n")
        ]
        if dalleTemplate:
            imagePrompts = [prompt.format(word=self.word) for prompt in imagePrompts]

        # fmt: off
        b64Images: list[str] = []
        async with asyncio.TaskGroup() as taskGroup:
            for imagePrompt in imagePrompts:
                async def imageGen():
                    dalleData = await dalleReq(
                        {
                            "prompt": imagePrompt,
                            "n": 1,
                            "size": "1024x1024",
                            "response_format": "b64_json",
                        },
                        self.session,
                    )
                    b64Images.append(dalleData)
                taskGroup.create_task(imageGen())
        # fmt: on

        images = []
        for i, image in enumerate(b64Images):
            image = Image(image, (1024, 1024), imagePrompts[i], dalleTemplate)
            images.append(image)

        self._images.extend(images)
        return {"images": images}

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
