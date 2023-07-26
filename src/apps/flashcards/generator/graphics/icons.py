import json
from dataclasses import dataclass


__all__ = ("icons",)

from ..utils.misc import fileAsBase64


@dataclass(slots=True, frozen=True)
class Icon:
    name: str
    path: str
    base64: str

    def __str__(self):
        return f"data:image/svg+xml;base64,{self.base64}"


with open("apps/flashcards/generator/graphics/icons/icons.json") as f:
    icons = {
        icon: Icon(
            name=icon,
            path=f"apps/flashcards/generator/graphics/icons/{icon}.svg",
            base64=fileAsBase64(f"apps/flashcards/generator/graphics/icons/{icon}.svg"),
        )
        for icon in json.load(f)
    }
