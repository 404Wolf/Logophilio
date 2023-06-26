__all__ = ("styles",)

from dataclasses import dataclass
from functools import cached_property
from importlib import import_module


@dataclass(frozen=True)
class Style:
    """
    A flashcard style

    Attributes:
        name: The name of the style.
        renderer: The renderer class for the style.
        sizes: The sizes available for the style.
    """

    name: str
    sizes: list[str]

    @cached_property
    def renderer(self):
        renderer_module = import_module(
            f".flashcards.renderers.styles.{self.name}.renderer", "src"
        )
        return getattr(renderer_module, f"{self.name.title()}Renderer")


styles = {
    "watercolor": Style(
        name="watercolor",
        sizes=["mini"],
    ),
}
