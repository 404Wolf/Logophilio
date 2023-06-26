import json
from contextlib import suppress
from dataclasses import dataclass

import jinja2

from src.flashcards.renderers import sizes, styles

__all__ = ("templates", "sizes")

jinjaEnv = jinja2.Environment(
    loader=jinja2.PackageLoader("flashcards", "renderers/styles"),
    autoescape=jinja2.select_autoescape(),
)
templates = {}


@dataclass(frozen=True, slots=True)
class Template:
    front: jinja2.Template
    back: jinja2.Template

    def renderFront(self, **kwargs) -> str:
        """
        Render the svg of a flashcard front side.

        Returns:
            str: The svg, as a string.
        """
        return self.front.render(**kwargs)

    def renderBack(self, **kwargs) -> str:
        """
        Render the svg of a flashcard back side.

        Returns:
            str: The svg, as a string.
        """
        return self.back.render(**kwargs)


for style in styles:
    for size in sizes:
        with suppress(FileNotFoundError):
            templates[f"{style}_{size}"] = Template(
                front=jinjaEnv.get_template(f"{style}/{size}/front.svg"),
                back=jinjaEnv.get_template(f"{style}/{size}/back.svg"),
            )
