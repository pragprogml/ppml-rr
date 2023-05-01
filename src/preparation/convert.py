"""Module for reading text files and converting them to a corpus of text documents."""

import logging
import os
from pathlib import Path

import smart_open

logger = logging.getLogger(__name__)


def get_file_contents(file_path: str) -> str:
    """
    Returns the contents of a file as a string.

    Args:
        file_path (str): The path to the file to read.

    Returns:
        str: A string containing the contents of the file.

    Raises:
        FileNotFoundError: If the file specified by `file_path` does not exist.
    """
    with smart_open.open(file_path, "r", encoding="utf-8") as file:
        text = file.read().rstrip()
    return text


def create_text_corpus(
    text_corpus_datadir: str, text_outfile_path: str, txt_input_directory: str
):
    """
    Creates a corpus of text documents by concatenating the contents of all text files in a directory.

    Args:
        text_corpus_datadir (str): The path to the directory where the output corpus file will be saved.
        text_outfile_path (str): The name of the output corpus file.
        txt_input_directory (str): The path to the directory containing the input text files.

    Returns:
        None

    Raises:
        FileNotFoundError: If the `txt_input_directory` does not exist.
        IsADirectoryError: If the `text_corpus_datadir` already exists as a directory.

    Example:
        create_text_corpus('/path/to/corpus/', 'corpus.txt', '/path/to/text/files/')

    """

    if not os.path.exists(text_corpus_datadir):
        os.makedirs(text_corpus_datadir)

    with smart_open.open(
        text_corpus_datadir + text_outfile_path, "w", encoding="utf-8"
    ) as outfile:
        for file in Path(txt_input_directory).glob("*.txt"):
            with smart_open.open(file, "r", encoding="utf-8") as infile:
                outfile.write(infile.read())
    logger.info(f"Generated corpus in: {text_corpus_datadir}{text_outfile_path}")
