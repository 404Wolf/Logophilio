from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class Image:
    """
    Image dataclass for storing image data.

    Attributes:
        base64 (str): Base64 encoded image.
        size (tuple[int, int]): Size of the image.
        prompt (str): Prompt for the image.
        dalleTemplate (str): Dalle template that the prompt was slotted into. This should
            include a {prompt} placeholder.
    """

    base64: str = field(repr=False)
    size: tuple[int, int]
    prompt: str
    dalleTemplate: str = field(repr=False)

    def __str__(self) -> str:
        return f"data:image/png;base64,{self.base64}"
