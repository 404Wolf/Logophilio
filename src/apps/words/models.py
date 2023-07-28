import asyncio
import base64

import aiohttp
from django.contrib.postgres.fields import ArrayField
from django.db import models

from .generator.generator import WordDataGenerator
from .utils.openai import gptReq, dalleReq


class WordImageConfig(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True)
    prompt = models.CharField(max_length=500)
    template = models.CharField(max_length=300)


class Word(models.Model):
    word = models.CharField(max_length=50, unique=True, primary_key=True)
    partOfSpeech = models.CharField(max_length=20)
    pronunciation = models.CharField(max_length=100)
    offensive = models.BooleanField(default=False)
    synonyms = ArrayField(models.CharField(max_length=50), size=8)
    antonyms = ArrayField(models.CharField(max_length=50), size=8)
    sentences = ArrayField(models.CharField(max_length=400), size=8)
    definitions = ArrayField(models.CharField(max_length=400), size=8)
    inspirationalQuotes = ArrayField(models.CharField(max_length=400), size=8)
    rhymes = ArrayField(models.CharField(max_length=50), size=8)
    notes = models.TextField(null=True)

    @classmethod
    async def generated(cls, word: str):
        async with aiohttp.ClientSession() as session:
            async with asyncio.TaskGroup() as taskGroup:
                generator = WordDataGenerator(word, session)

                # fmt:off
                wordData = {
                    "word": word,
                    "partOfSpeech": taskGroup.create_task(generator.partOfSpeech()),
                    "pronunciation": taskGroup.create_task(generator.pronunciation()),
                    "offensive": taskGroup.create_task(generator.offensive()),
                    "synonyms": taskGroup.create_task(generator.synonyms()),
                    "antonyms": taskGroup.create_task(generator.antonyms()),
                    "sentences": taskGroup.create_task(generator.sentences()),
                    "definitions": taskGroup.create_task(generator.definitions()),
                    "inspirationalQuotes": taskGroup.create_task(generator.inspirationalQuotes()),
                    "rhymes": taskGroup.create_task(generator.rhymes()),
                }
                # fmt:on
        for key, value in wordData.items():
            if isinstance(value, asyncio.Task):
                wordData[key] = value.result()
        return cls(**wordData)


class WordImage(models.Model):
    word = models.ForeignKey(Word, on_delete=models.SET_NULL, null=True)
    width = models.IntegerField()
    height = models.IntegerField()
    notes = models.TextField(null=True)
    image = models.ImageField(null=True)

    @classmethod
    async def generated(cls, word: Word, config: WordImageConfig):
        async with aiohttp.ClientSession() as session:
            imagePrompt = await gptReq(
                {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "user",
                            "content": config.prompt.format(word=word.word, count=1),
                        }
                    ],
                },
                session,
            )
            imageB64 = await dalleReq(
                {
                    "prompt": imagePrompt,
                    "n": 1,
                    "size": "1024x1024",
                    "response_format": "b64_json",
                },
                session,
            )

        return cls(word=word, width=1024, height=1024, image=base64.b64decode(imageB64))
