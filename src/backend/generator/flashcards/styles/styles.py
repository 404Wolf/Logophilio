import json
from dataclasses import dataclass

import jinja2

__all__ = ("styles",)

jinjaEnv = jinja2.Environment(
    loader=jinja2.PackageLoader("flashcards", "styles"),
    autoescape=jinja2.select_autoescape(),
)


@dataclass(frozen=True, slots=True)
class Style:
    """
    A specific flashcard style.

    Attributes:
        name: The name of the style.
        front: The front template of the flashcard.
        back: The back template of the flashcard.
        size: The size of the flashcard, as a tuple of (width, height).
        config: The configuration of the style.
    """

    name: str
    front: jinja2.Template
    back: jinja2.Template
    size: tuple[int, int]
    config: dict[str, dict]

    @classmethod
    def fromName(cls, name: str) -> "Style":
        """
        Load a style from its name.

        Args:
            name: The name of the style.

        Returns:
            The style.
        """
        with open(f"flashcards/styles/{name}/config.json") as f:
            styleConfig = json.load(f)
        return cls(
            name=name,
            front=jinjaEnv.get_template(f"{name}/front.svg"),
            back=jinjaEnv.get_template(f"{name}/back.svg"),
            size=(styleConfig["size"]["width"], styleConfig["size"]["height"]),
            config=styleConfig["generation"],
        )


styles = {
    "watercolor": Style.fromName("watercolor"),
}
