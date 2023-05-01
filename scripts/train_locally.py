#!/usr/bin/env python3
"""Local training for development."""

import logging
import os
import sys
import uuid
import tempfile

import mlflow

# sys.path.insert(0, os.path.abspath("src/training"))
sys.path.insert(0, os.path.abspath("src"))

from ingestion.download import convert_pdf_to_text

# pylint: disable=C0413,W0012,W0611
from preparation.convert import get_file_contents
from training import (
    GensimWord2VecModel,
    evaluate_similarity,
    load_word2vec_model,
    train_and_track_experiment,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def evaluate_similarity_of_some_domain_words(model):
    """
    Evaluates the similarity of some domain-specific word pairs using a word2vec model.

    :param model: The word2vec model to use for evaluation.
    :type model: gensim.models.word2vec.Word2Vec
    """

    evaluate_similarity(model.wv, "causal", "sem")
    evaluate_similarity(model.wv, "stratified", "stratification")
    evaluate_similarity(model.wv, "causal_hierarchy", "causal_hierarchy")
    evaluate_similarity(model.wv, "causal_hierarchy", "sem")
    evaluate_similarity(model.wv, "sem", "stratified")
    evaluate_similarity(model.wv, "experimental", "observational")
    evaluate_similarity(model.wv, "backdoor", "do_calculus")
    evaluate_similarity(model.wv, "latent", "confounding")
    evaluate_similarity(model.wv, "latent", "unobserved_confounder")
    evaluate_similarity(model.wv, "latent", "unobserved_confounding")


def run_evaluation_with_unwrapped_model(
    document_path: str, model_path: str, domain_keywords_path: str
):
    """
    Runs an evaluation using a pre-trained word2vec model and a list of domain-specific keywords.

    :param document_path: The path of the document to evaluate.
    :type document_path: str
    :param domain_keywords_path: The path of the file containing domain-specific keywords.
    :type domain_keywords_path: str
    """

    model = load_word2vec_model(model_path)

    model = GensimWord2VecModel(model, domain_keywords_path)
    tokens = get_file_contents(document_path)
    similarity_score = model.predict("", tokens)
    logging.info(f"Similarity score : {similarity_score}")

    evaluate_similarity_of_some_domain_words(model.word2vec_model)


def run_evaluation_with_mlflow(document_path: str):
    """
    Runs an evaluation using a word2vec model trained and tracked with MLflow.

    :param document_path: The path of the document to evaluate.
    :type document_path: str
    """

    if "TEXT_CORPUS_DATADIR" in os.environ:
        text_corpus_datadir = os.environ["TEXT_CORPUS_DATADIR"]
    else:
        logger.info("The TEXT_CORPUS_DATADIR environment variable does not exist.")

    if "TEXT_CORPUS_FNAME" in os.environ:
        text_corpus_fname = os.environ["TEXT_CORPUS_FNAME"]
    else:
        logger.info("The TEXT_CORPUS_FNAME environment variable does not exist.")

    if "DOMAIN_KEYWORDS" in os.environ:
        domain_keywords_path = os.environ["DOMAIN_KEYWORDS"]
    else:
        logger.info("The DOMAIN_KEYWORDS environment variable does not exist.")

    model_s3_path = train_and_track_experiment(
        model_uri=str(uuid.uuid4().hex)[:8],
        text_corpus=text_corpus_datadir + text_corpus_fname,
        domain_keywords=domain_keywords_path,
    )

    model = mlflow.pyfunc.load_model(model_s3_path)

    tokens = get_file_contents(document_path)
    similarity_score = model.predict(tokens)
    logging.info(f"Similarity score : {similarity_score}")

    unwrapped_model = model.unwrap_python_model()
    evaluate_similarity_of_some_domain_words(unwrapped_model.word2vec_model)


def main():
    """
    Runs the ingestion, training and evaluation steps locally in development.
    """

    SAMPLE_ARTICLE = "2103.01035"

    convert_pdf_to_text(
        "resources/benchmark/valid/" + SAMPLE_ARTICLE + ".pdf",
        tempfile.gettempdir(),
    )
    run_evaluation_with_mlflow(tempfile.gettempdir() + SAMPLE_ARTICLE + ".txt")

    # run evaluation with a pre-trained unwrapped model

    # domain_keywords_path = ""
    # if "DOMAIN_KEYWORDS" in os.environ:
    #     domain_keywords_path = os.environ["DOMAIN_KEYWORDS"]
    # else:
    #     logger.info("The DOMAIN_KEYWORDS environment variable does not exist.")

    # run_evaluation_with_unwrapped_model(
    #     "/tmp/2208.11128.txt",
    #     "/var/folders/gb/8txsdzs54rgb0dry1fbn50dr0000gn/T/model_artifact__zun8rlr",
    #     domain_keywords_path,
    # )


if __name__ == "__main__":
    main()
#
