import json

__all__ = ("styles", "templates")

with open("flashcards/renderer/styles/styles.json") as f:
    styles = json.load(f)

from .templates import templates
