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
        front: The front of the flashcard.
        back: The back of the flashcard.
        aesthetic: The aesthetic of the flashcard. This is a template with a {prompt}
            placeholder, that tells DALLE how to style the image.
        fields: The number of items needed for each field to generate the flashcard.
    """

    name: str
    front: jinja2.Template
    back: jinja2.Template
    aesthetic: jinja2.Template
    fields: dict[str, int]

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
            aesthetic=jinjaEnv.from_string(styleConfig["aesthetic"]),
            fields=styleConfig["fields"],
        )


styles = {
    "watercolor": Style.fromName("watercolor"),
}
