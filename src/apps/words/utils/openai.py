import os

import aiohttp
from dotenv import load_dotenv

load_dotenv()

CHAT_COMPLETIONS_API = "https://api.openai.com/v1/chat/completions"
DALLE_API = "https://api.openai.com/v1/images/generations"
OPENAI_KEY = os.getenv("OPENAI")

class OpenAiApiReqError(Exception):
    """
    Raised when an error occurs while making an API request.
    """

    pass


async def gptReq(reqData: dict, session: aiohttp.ClientSession) -> str:
    """
    Use GPT to generate text.

    Args:
        reqData: The request data.
        session: The aiohttp session.

    Returns:
        The generated text.
    """
    for attempt in range(6):
        async with session.post(
            CHAT_COMPLETIONS_API,
            headers={"Authorization": f"Bearer {OPENAI_KEY}"},
            json=reqData,
        ) as resp:
            try:
                return (await resp.json())["choices"][0]["message"]["content"]
            except KeyError:
                if attempt < 10:
                    raise OpenAiApiReqError(await resp.text())


async def dalleReq(reqData: dict, session: aiohttp.ClientSession) -> str:
    """
    Use DALLE to generate an image.

    Args:
        reqData: The request data.
        session: The aiohttp session.

    Returns:
        The generated image.
    """
    reqData["response_format"] = "b64_json"
    async with session.post(
        DALLE_API,
        headers={"Authorization": f"Bearer {OPENAI_KEY}"},
        json=reqData,
    ) as resp:
        try:
            return (await resp.json())["data"][0]["b64_json"]
        except KeyError:
            raise OpenAiApiReqError(await resp.text())
