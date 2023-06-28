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
        dalleTemplate: The dalle template to use for generating images for the style of
            the flashcard; should include the a {PROMPT} placeholder.
        fieldKwargs: The keyword-arguments to pump through the flashcard data generator.
            includes kwargs like 'count,' and 'boldWord.'
    """

    name: str
    front: jinja2.Template
    back: jinja2.Template
    dalleTemplate: jinja2.Template
    fieldSettings: dict[str, dict[str, object]] = None

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
            dalleTemplate=styleConfig["dalleTemplate"],
        )


styles = {
    "watercolor": Style.fromName("watercolor"),
}
