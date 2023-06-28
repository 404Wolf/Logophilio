PromptType = dict[str, str | int | list[str] | list[dict[str, str | int]]]


def dalleImagePrompt(word: str, count: int) -> PromptType:
    return {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": f'Provide {count} brief, different bits of imagery that capture a common occurrence of "{word}" These descriptions should: - NOT use the word "{word}."\n- NOT involve humans.\n- BE 300 characters or less.',
            }
        ],
    }


def partOfSpeechPrompt(word: str) -> PromptType:
    return {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a very knowledgeable librarian who is very good at pronouncing words, and follows instructions concisely and well. You always respond from the following options: noun, verb, adjective, adverb, pronoun, preposition, conjunction, interjection, determiner, or article.",
            },
            {
                "role": "system",
                "content": "Always respond all lowercase, with one word. Never add a prefix or suffix, or any filler text. Only respond with one of the options above. Only.",
            },
            {
                "role": "user",
                "content": f"What part of speech is the word {word}?",
            },
        ],
        "max_tokens": 30 * 3,
        "temperature": 0.7,
        "presence_penalty": 0.4,
        "frequency_penalty": 0.6,
    }


def pronunciationPrompt(word: str) -> PromptType:
    return {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a very knowledgeable librarian who is very good at pronouncing words, and follows instructions concisely and well. You always respond with the pronunciation of the word",
            },
            {
                "role": "system",
                "content": "Always respond all lowercase, with one word, separated phonetically by hyphens. Do not add any prefix or suffix text. Only respond with a hyphenated pronunciation.",
            },
            {
                "role": "user",
                "content": f"What is the pronunciation of the word {word}?",
            },
        ],
        "max_tokens": 30 * 3,
        "temperature": 0.7,
        "presence_penalty": 0.4,
        "frequency_penalty": 0.6,
    }


def synonymPrompt(word: str, count: int) -> PromptType:
    return {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a very knowledgeable librarian that helps people learn words. You follow instructions exactly as given.",
            },
            {
                "role": "user",
                "content": f"Provide {count} synonyms for the word {word}, separated by newlines.",
            },
        ],
        "max_tokens": 30 * 3,
        "temperature": 0.7,
        "presence_penalty": 0.4,
        "frequency_penalty": 0.6,
    }


def antonymPrompt(word: str, count: int) -> PromptType:
    return {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a very knowledgeable librarian that helps people learn words. You follow instructions exactly as given.",
            },
            {
                "role": "user",
                "content": f"Provide {count} antonyms for the word {word}, separated by newlines.",
            },
        ],
        "max_tokens": 30 * 3,
        "temperature": 0.7,
        "presence_penalty": 0.4,
        "frequency_penalty": 0.6,
    }


def definitionPrompt(word: str, count: int) -> PromptType:
    return {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a very knowledgeable librarian that helps people understand the meaning of words. You follow instructions exactly as given.",
            },
            {
                "role": "user",
                "content": f"Provide {count} definitions for the word {word}, separated by newlines.",
            },
        ],
        "max_tokens": 30 * 3,
        "temperature": 0.7,
        "presence_penalty": 0.4,
        "frequency_penalty": 0.6,
    }


def sentencePrompt(word: str, count: int) -> PromptType:
    return {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a wise poet who writes short disparate sentences "
                "using particular words.",
            },
            {
                "role": "user",
                "content": f"Give me {count} sentences using the word {word}, separated by newlines.",
            },
        ],
        "max_tokens": 30 * 3,
        "temperature": 0.7,
        "presence_penalty": 0.4,
        "frequency_penalty": 0.6,
    }


def inspirationalQuotePrompt(word: str, count: int) -> PromptType:
    return {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a very famous speaker who says many great and deeply inspiring things. Each of your quotes embraces a specific word, and is flavored towards that word. You're also known to be very pithy when you speak, so each of your quotes is a short-ish sentence.",
            },
            {
                "role": "system",
                "content": "Each time you respond, you must provide a new and unique quote.",
            },
            {
                "role": "user",
                "content": f"Give me {count} inspirational quotes using the word {word}, separated by newlines.",
            },
        ],
        "max_tokens": 30 * 3,
        "temperature": 0.7,
        "presence_penalty": 0.4,
        "frequency_penalty": 0.6,
    }


def originPrompt(word: str) -> PromptType:
    return {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a good historian who is very pithy and articulate. You follow instructions exactly as given, and provide down-to-the-point origins of words provided. You do not restate the question, and you provide a single sentence response that is clear and accurate.",
                "role": "user",
                "content": f'In one pithy sentence that doesn\'t restate the question, what is the origin of the word "{word}"?',
            }
        ],
        "max_tokens": 30 * 3,
        "temperature": 0.7,
        "presence_penalty": 0.4,
        "frequency_penalty": 0.6,
    }


def rhymingPrompt(word: str, count: int) -> PromptType:
    return {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a musician who is very good at rhyming words, and follows instructions concisely and well.",
            },
            {
                "role": "user",
                "content": f"Give me {count} words that rhyme with {word}, separated by newlines.",
            },
        ],
        "max_tokens": 30 * 3,
        "temperature": 0.7,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0,
    }


def offensivePrompt(word: str) -> PromptType:
    return {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a moderator. You only respond with 'yes' or 'no,' without punctuation or any other words in your responses.",
            },
            {
                "role": "user",
                "content": f'is {word} an offensive word? answer with "yes" or "no" only with no other words or punctuation',
            },
        ],
        "max_tokens": 30 * 3,
        "temperature": 0.3,
    }
