import json

from src.flashcards.renderer.utils import file_as_base64

__all__ = ("icons")

with open("flashcards/graphics/icons/icons.json") as f:
    icons = {
        style: file_as_base64(f"flashcards/graphics/icons/{style}.svg")
        for style in json.load(f)
    }
