"""RESTful API endpoint with BentoML for serving the PPML-RR (Recommending Recommendations) use-case."""

from __future__ import annotations

import io
import logging
import os
import sys
from typing import Any

import bentoml
from bentoml.exceptions import BentoMLException
from bentoml.io import JSON, File
from pypdf import PdfReader
from pypdf.errors import PdfReadError

sys.path.append(os.path.abspath("src"))
sys.path.append(os.path.abspath("src/training"))

from preparation.clean import combined_text_cleaning

from training import *

ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)

bentoml_logger = logging.getLogger("bentoml")
bentoml_logger.addHandler(ch)
bentoml_logger.setLevel(logging.INFO)

if "BENTO_MODEL" in os.environ:
    BENTO_MODEL = os.getenv("BENTO_MODEL")
else:
    bentoml_logger.info("The BENTO_MODEL environment variable does not exist.")

runner = bentoml.mlflow.get(BENTO_MODEL).to_runner()

svc = bentoml.Service("ppml_rr", runners=[runner])


@svc.api(input=File(), output=JSON())
def classify(stream: io.BytesIO[Any]) -> str:
    """
    Classifies the text content of a PDF file using a pre-trained model.

    Args:
        stream (io.BytesIO): A byte stream containing the contents of the PDF file to classify.
    Returns:
        json: A score between the text content of the PDF file vs the training corpus.

    Raises:
        BentoMLException: If the input file is not a PDF file.
    """
    content = ""
    reader = ""
    with stream as pdf:
        try:
            reader = PdfReader(pdf)
        except PdfReadError as exc:
            raise BentoMLException("The file is not a PDF file.") from exc

        for page_num, page in enumerate(reader.pages):
            bentoml_logger.info(f"Processing page {page_num+1}...")
            content += page.extract_text()

    tokens = combined_text_cleaning(content)
    # add ngrams
    similarity_score = runner.predict.run(tokens)

    bentoml_logger.info(f"Similarity score: {similarity_score}")
    return {"value": similarity_score}
