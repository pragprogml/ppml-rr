#!/usr/bin/env python3

"""Downloading and processing arXiv articles for local ingestion in development."""

import logging
import os
import sys

sys.path.insert(0, os.path.abspath("src"))

# pylint: disable=C0413,W0012,W0611
from ingestion.download import (
    articles_download,
    convert_pdf_to_text_in_parallel,
    # convert_pdf_to_text_in_sequential,
)

from preparation.convert import create_text_corpus


def main():
    """
    Downloading and processing arXiv articles for local ingestion in development"
    """

    env_vars = {
        "ARXIV_ARTICLE_LIST_SMALL10": "arxiv_article_list_small",
        "PDF_DATADIR": "pdf_datadir",
        "TXT_DATADIR": "txt_datadir",
        "TEXT_CORPUS_DATADIR": "text_corpus_datadir",
        "TEXT_CORPUS_FNAME": "text_corpus_fname",
    }

    for env_var, var_name in env_vars.items():
        if env_var in os.environ:
            globals()[var_name] = os.getenv(env_var)
        else:
            logger.info(f"The {env_var} environment variable does not exist, exiting.")

    articles_download(globals()["arxiv_article_list_small"], globals()["pdf_datadir"])

    convert_pdf_to_text_in_parallel(globals()["pdf_datadir"], globals()["txt_datadir"])

    # convert_pdf_to_text_in_sequential(
    #     globals()["pdf_datadir"], globals()["txt_datadir"]
    # )

    create_text_corpus(
        globals()["text_corpus_datadir"],
        globals()["text_corpus_fname"],
        globals()["txt_datadir"],
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    main()
