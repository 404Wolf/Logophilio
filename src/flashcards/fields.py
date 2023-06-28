from dataclasses import dataclass, field


@dataclass(slots=True)
class FlashcardFields:
    """
    Fields of a flashcard.

    Attributes:
        partOfSpeech: The part of speech of the word.
        pronunciation: The pronunciation of the word.
        synonyms: The synonyms of the word.
        antonyms: The antonyms of the word.
        sentences: The sentences of the word.
        definitions: The definitions of the word.
        inspirationalQuotes: Inspirational quotes using the word.
        rhyming: The rhyming words of the word.
        origin: The origin of the word.
        images: Images of the word.
        offensive: Whether the word is offensive.
    """

    partOfSpeech: str = None
    pronunciation: str = None
    origin: str = None
    synonyms: list[str] = field(default_factory=list)
    antonyms: list[str] = field(default_factory=list)
    sentences: list[str] = field(default_factory=list)
    definitions: list[str] = field(default_factory=list)
    inspirationalQuotes: list[str] = field(default_factory=list)
    rhyming: list[str] = field(default_factory=list)
    images: list["FlashcardFields.Image"] = field(default_factory=list)
    offensive: bool = None

    @dataclass(frozen=True, slots=True)
    class Image:
        base64: str
        size: tuple[int, int]
        prompt: str
        style: str
