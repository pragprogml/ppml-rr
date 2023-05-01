"""Preparations functions."""

import logging
import re
from functools import reduce

from cleantext import clean
from gensim.models.phrases import ENGLISH_CONNECTOR_WORDS, Phrases
from gensim.parsing.preprocessing import remove_stopwords
from gensim.utils import simple_preprocess

logger = logging.getLogger(__name__)


def combined_text_cleaning(text: str) -> str:
    """
    Cleans a list of text documents and returns a combined string of unique words.

    Parameters:
    -----------
    text : list of str
        A list of text documents to clean.

    Returns:
    --------
    str
        A string of unique words after cleaning.

    Notes:
    ------
    The function uses the `clean` method from the `clean_text` library to clean the text.
    It removes unnecessary characters, numbers, punctuations, and stop words.
    It also replaces some text patterns (URLs, emails, phone numbers, etc.) with spaces.
    Finally, it combines the cleaned text into a string of unique words, removing any duplicates.
    """

    patterns = [
        (r"[^a-zA-Z]+", " "),
        (r"(\\b[A-Za-z] \\b|\\b [A-Za-z]\\b)", " "),
        (r"\b\w{1,2}\b", " "),
    ]

    clean_text = clean(
        text,
        fix_unicode=True,
        lang="en",
        lower=True,
        no_currency_symbols=True,
        no_digits=True,
        no_emails=True,
        no_emoji=True,
        no_line_breaks=True,
        no_numbers=False,
        no_phone_numbers=True,
        no_punct=True,
        no_urls=True,
        normalize_whitespace=True,
        replace_with_currency_symbol=" ",
        replace_with_digit=" ",
        replace_with_email=" ",
        replace_with_number=" ",
        replace_with_phone_number=" ",
        replace_with_punct=" ",
        replace_with_url=" ",
        to_ascii=True,
    )

    clean_text = reduce(
        lambda t, pattern: re.sub(pattern[0], pattern[1], t), patterns, clean_text
    )

    clean_text = remove_stopwords(clean_text)

    logger.info(
        f"Text size reduced by from {len(text.split())} to {len(clean_text.split())}"
    )

    return clean_text


def clean_stopwords_str(text: str) -> list:
    """Remove stopword from a string using gensim's remove_stopwords function."""

    without_stopwords = remove_stopwords(text)
    without_accent_and_with_minlen = simple_preprocess(
        doc=without_stopwords, deacc=True, min_len=3, max_len=40
    )

    return [without_accent_and_with_minlen]


def get_bigram(tokens: list) -> list:
    """Return a text with bigrams based on gensim's Phrases function."""

    bigrams = Phrases(
        tokens, min_count=5, threshold=10.0, connector_words=ENGLISH_CONNECTOR_WORDS
    )
    texts = [bigrams[line] for line in tokens]
    return texts


def get_bigram_from_vocabulary(vocabulary: list, text: str):
    """
    Replaces unigrams in the given text with their corresponding bigrams from the vocabulary.

    Args:
        vocabulary (list): A list of n-grams
        text (str): The input text where unigrams will be replaced with bigrams.

    Returns:
        str: The input text with unigrams replaced by n-grams from the vocabulary.

    Example:
        vocabulary = [["machine_learning", "deep_learning"]]
        text = "Working with machine learning and deep learning."
        get_bigram_from_vocabulary(vocabulary, text)
    """

    vocabulary_words = [item for sublist in vocabulary for item in sublist]

    replace = []
    for word in vocabulary_words:
        replace.append((re.sub("_", " ", word), word))

    for old_token, new_token in replace:
        text = re.sub(old_token, new_token, text)

    return text
