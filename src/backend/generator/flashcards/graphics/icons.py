import json
from dataclasses import dataclass

from src.flashcards.utils.misc import fileAsBase64

__all__ = ("icons",)


@dataclass(slots=True, frozen=True)
class Icon:
    name: str
    path: str
    base64: str

    def __str__(self):
        return f"data:image/svg+xml;base64,{self.base64}"


with open ("flashcards/graphics/icons/icons.json") as f:
    icons = {
        icon: Icon(
            name=icon,
            path=f"flashcards/graphics/icons/{icon}.svg",
            base64=fileAsBase64(f"flashcards/graphics/icons/{icon}.svg"),
        )
        for icon in json.load(f)
    }
