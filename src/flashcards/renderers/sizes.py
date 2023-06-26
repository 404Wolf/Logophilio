from dataclasses import dataclass

__all__ = ("sizes",)


@dataclass(slots=True, frozen=True)
class Size:
    """
    A flashcard size

    Attributes:
        name: The name of the size.
        dimensions: The dimensions of the size.
    """

    name: str
    pixel_dimensions: tuple[float, float]
    imperial_dimensions: tuple[float, float]


sizes = {
    "mini": Size(
        name="mini",
        pixel_dimensions=(180, 126),
        imperial_dimensions=(2.5, 1.75),
    ),
}
