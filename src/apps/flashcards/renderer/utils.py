import re


def boldWordOccurances(string: str, word: str):
    def _handleOccurance(occurance):
        return f"<bold>{occurance.group()}</bold>"

    return re.sub(f"{word}", _handleOccurance, string)

def startOutUpper(string: str):
    return string[0].upper() + string[1:]

partOfSpeechAbbreviations = {
    "noun": "noun",
    "verb": "verb",
    "adjective": "adj",
    "adverb": "adv",
    "pronoun": "pron",
    "preposition": "prep",
    "conjunction": "conj",
    "interjection": "intj",
    "article": "artl",
    "numeral": "numr",
    "infinitive": "infi",
    "participle": "part",
    "gerund": "gerd",
    "prefix": "pref",
    "suffix": "suff",
    "abbreviation": "abbr",
    "acronym": "acro",
    "initialism": "init",
    "phrase": "phra",
    # Add more mappings as needed
}