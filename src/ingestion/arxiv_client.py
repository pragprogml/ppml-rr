"""This module provides a client for downloading articles from arXiv."""

import logging
import os

import arxiv
import smart_open
from parfive import Downloader
from retry import retry

PARFIVE_DELAY = os.getenv("PARFIVE_DELAY", "5")
PARFIVE_BACKOFF = os.getenv("PARFIVE_BACKOFF", "2")


class ParfiveClientError(Exception):
    """
    An exception class that is raised when there is an error downloading articles using the Parfive library.
    """


class ArxivClient:

    """
    A client for downloading articles from arXiv, an open-access repository of electronic preprints and postprints
    approved for posting after moderation, but not peer review.

    :param max_connection: The maximum number of connections to use for downloading articles.
    :type max_connection: int
    :param max_results: The maximum number of search results to retrieve from arXiv.
    :type max_results: float
    """

    max_connection: int
    urls: list
    max_results: float

    def __init__(self, max_connection: int, max_results: float):
        """
        Initializes the ArxivClient object with the given max_connection and max_results values.

        :param max_connection: The maximum number of connections to use for downloading articles.
        :type max_connection: int
        :param max_results: The maximum number of search results to retrieve from arXiv.
        :type max_results: float
        """

        self.max_connection = max_connection
        self.max_results = max_results
        self.urls = []
        self.logger = logging.getLogger(__name__)

    def query(self, query: str):
        """
        Executes a query to arXiv and appends the URLs of the resulting articles to the object's list of URLs.

        :param query: The query to execute on arXiv.
        :type query: str
        """

        arxiv_client = arxiv.Search(
            query=query,
            max_results=self.max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )
        for article in arxiv_client.results():
            self.urls.append(article.pdf_url + ".pdf")

    @retry(ParfiveClientError, delay=PARFIVE_DELAY, backoff=PARFIVE_BACKOFF)
    def get(self, path: str) -> list:
        """
        Downloads the PDFs of the articles from arXiv and saves them to the given path using the Parfive library.

        :param path: The path where the PDFs should be saved.
        :type path: str
        :return: A list of Parfive download results.
        :rtype: list
        :raises ParfiveClientError: If there is an error downloading the articles using Parfive.
        """

        parfive_client = Downloader(
            max_conn=self.max_connection,
            progress=False,
            overwrite=False,
        )
        for url in self.urls:
            self.logger.info(f"Downloading arXiv article from URL {url} into {path}")
            parfive_client.enqueue_file(url, path, overwrite=False)

        self.logger.info(
            f"Download using Parfive library with {PARFIVE_DELAY} secs of delay and {PARFIVE_BACKOFF} backoff"
        )

        results = parfive_client.download()

        return results

    def save_article_url_to_file(self, path: str):
        """
        Saves the list of articles' URLs to a file at the given path.

        :param path: The path of the file to save the URLs to.
        :type path: str
        :raises OSError: If there is an error saving the file due to an OS-related issue.
        :raises IOError: If there is an error saving the file due to an I/O-related issue.
        """

        try:
            with smart_open.open(path, "w", encoding="utf-8") as filehandle:
                for url in self.urls:
                    filehandle.write(url + "\n")
        except (OSError, IOError) as exception:
            self.logger.exception(
                f"Unable to save article list on {path}", exc_info=exception
            )

    def load_article_url_from_file(self, path: str):
        """
        Loads the list of articles' URLs from a file at the given path and appends them to the object's list of URLs.

        :param path: The path of the file to load the URLs from.
        :type path: str
        :raises OSError: If there is an error loading the file due to an OS-related issue.
        :raises IOError: If there is an error loading the file due to an I/O-related issue.
        """

        try:
            with smart_open.open(path, encoding="utf-8") as file:
                for url in file.read().splitlines():
                    self.urls.append(url)
        except (OSError, IOError) as exception:
            self.logger.exception(
                f"Unable to read article list on {path}", exc_info=exception
            )
