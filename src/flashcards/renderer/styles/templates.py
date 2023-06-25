import json
from dataclasses import dataclass

import jinja2

from src.flashcards.renderer.styles import styles

__all__ = ("templates",)

jinjaEnv = jinja2.Environment(
    loader=jinja2.PackageLoader("flashcards", "renderer/styles"),
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
    with open(f"flashcards/renderer/styles/{style}/sizes.json") as f:
        sizes = json.load(f)

    for size in sizes:
        templates[f"{style}_{size}"] = Template(
            front=jinjaEnv.get_template(f"{style}/{size}/front.svg"),
            back=jinjaEnv.get_template(f"{style}/{size}/back.svg"),
        )