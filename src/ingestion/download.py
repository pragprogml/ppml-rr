"""Download and conversion module."""

import logging
import multiprocessing as mp
import os
import timeit
from collections import UserList
from itertools import repeat
from pathlib import Path

from ingestion import ArxivClient, Pdf
from preparation.clean import combined_text_cleaning

logger = logging.getLogger(__name__)


def articles_download(
    urls_file_path: str,
    pdf_output_directory: str,
    arxiv_query: str = "",
) -> UserList:
    """
    Downloads a list of articles from arXiv and saves their PDF files to the given output directory.

    :param urls_file_path: The path of the file where the list of article URLs should be saved or loaded from.
    :type urls_file_path: str
    :param pdf_output_directory: The directory where the downloaded PDF files should be saved.
    :type pdf_output_directory: str
    :param arxiv_query: An optional query string to use when downloading articles from arXiv.
    :type arxiv_query: str
    :return: A list of Parfive download results.
    :rtype: UserList
    """

    if not os.path.exists(pdf_output_directory):
        os.makedirs(pdf_output_directory)

    arxiv_client = ArxivClient(max_connection=2, max_results=10)

    if os.path.exists(urls_file_path):
        logger.info("Download from arXiv with a list of article from file")
        arxiv_client.load_article_url_from_file(urls_file_path)

    else:
        logger.info(
            "Download from arXiv with an arXiv query (may be slow due to rate limiting imposed by arXiv)"
        )
        arxiv_client.query(arxiv_query)
        arxiv_client.save_article_url_to_file(urls_file_path)

    arxiv_client.get(pdf_output_directory)


def convert_pdf_to_text(pdf_file_path: str, txt_output_directory: str):
    """
    Converts a PDF file into text and saves it to a file in the given output directory.

    :param pdf_file_path: The path of the PDF file to convert.
    :type pdf_file_path: str
    :param txt_output_directory: The directory where the output text file should be saved.
    :type txt_output_directory: str
    """

    if not os.path.exists(txt_output_directory):
        os.makedirs(txt_output_directory)

    pdf_file = Pdf(pdf_file_path)
    pdf_file.to_text()
    pdf_file.content = combined_text_cleaning(pdf_file.content)
    pdf_file.save(destination_path=txt_output_directory)


def convert_pdf_to_text_in_sequential(
    pdf_input_directory: str, txt_output_directory: str
):
    """
    Converts all PDF files in a given input directory to text files in the given output directory, in sequential mode.

    :param pdf_input_directory: The directory containing the PDF files to convert.
    :type pdf_input_directory: str
    :param txt_output_directory: The directory where the output text files should be saved.
    :type txt_output_directory: str
    """

    start = timeit.default_timer()
    for pdf_file in Path(pdf_input_directory).glob("*.pdf"):
        logger.info(f"Converting PDF file from {pdf_file} into {txt_output_directory}")
        convert_pdf_to_text(pdf_file, txt_output_directory)
    stop = timeit.default_timer()
    logger.info(f"Elapsed time for conversion: {stop - start}")


def convert_pdf_to_text_in_parallel(
    pdf_input_directory: str, txt_output_directory: str
):
    """
    Converts all PDF files in a given input directory to text files in the given output directory, in parallel mode.

    :param pdf_input_directory: The directory containing the PDF files to convert.
    :type pdf_input_directory: str
    :param txt_output_directory: The directory where the output text files should be saved.
    :type txt_output_directory: str
    """

    pdfs = []
    for file in Path(pdf_input_directory).glob("*.pdf"):
        pdfs.append(str(file.absolute()))

    start = timeit.default_timer()
    with mp.Pool() as pool:
        pool.starmap(
            convert_pdf_to_text, zip(pdfs, repeat(txt_output_directory)), chunksize=1
        )
    stop = timeit.default_timer()
    logger.info(f"Elapsed time for conversion: {stop - start}")
