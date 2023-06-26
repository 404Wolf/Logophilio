import json

from src.flashcards.renderers.utils import fileAsBase64

__all__ = ("icons",)

with open("flashcards/graphics/icons/icons.json") as f:
    icons = {
        style: fileAsBase64(f"flashcards/graphics/icons/{style}.svg")
        for style in json.load(f)
    }
