"""Training module."""
import logging
import os
import platform
import sys
import tempfile
import requests

import gensim
import mlflow
import mlflow.pyfunc
import numpy as np
import smart_open
from gensim.models import KeyedVectors, Word2Vec
from gensim.models.callbacks import CallbackAny2Vec
from gensim.utils import RULE_KEEP
from scipy.spatial import distance

sys.path.insert(0, os.path.abspath("src"))

# pylint: disable=C0413
from preparation.clean import (
    clean_stopwords_str,
    get_bigram,
    get_bigram_from_vocabulary,
)

# pylint: disable=C0413
from preparation.convert import get_file_contents

logger = logging.getLogger(__name__)


class GensimWord2VecModel(mlflow.pyfunc.PythonModel):
    """A wrapper class for the Gensim Word2Vec model to be used with MLflow."""

    def __init__(self, word2vec_model, domain_keywords_path):
        """Initialize the GensimWord2VecModel class."""
        self.word2vec_model = word2vec_model
        self.domain_keywords_path = domain_keywords_path
        self.logger = logging.getLogger(__name__)

    # pylint: disable=R0914
    def predict(self, context, model_input: str) -> float:
        """Predict the similarity score of a document with a domain-specific vocabulary."""
        vocabulary = get_domain_keywords(self.domain_keywords_path)
        text = get_bigram_from_vocabulary(vocabulary, model_input)
        tokens = clean_stopwords_str(text)
        text = get_bigram(tokens)

        # train word2vec on the document to be analysed
        (model, trained_word_count, raw_word_count) = train_word2vec(text, vocabulary)

        self.logger.info(f"Training on {raw_word_count} total raw words")
        self.logger.info(f"Effective words : {trained_word_count}")

        if trained_word_count == 0:
            return 0.0

        # get the words that match both in the document and in the vocabulary
        word_match_with_vocabulary = []
        for word in text[0]:
            for keyword in vocabulary[0]:
                if word == keyword:
                    word_match_with_vocabulary.append(word)

        self.logger.info(
            f"Matched word count from vocabulary: {len(word_match_with_vocabulary)}"
        )
        self.logger.info(f"Matched words in vocabulary: {word_match_with_vocabulary}")

        matrix = np.full((len(vocabulary[0]), len(word_match_with_vocabulary)), 0.0)

        for i, word_vocab in enumerate(vocabulary[0]):
            for j, word_vocab_match in enumerate(word_match_with_vocabulary):
                matrix[i][j] = 1 - distance.cosine(
                    self.word2vec_model.wv.get_vector(word_vocab),
                    model.wv.get_vector(word_vocab_match),
                )

        matrix_mean = np.mean(matrix, axis=0)
        matrix_max = np.max(matrix, axis=0)

        self.logger.info(f"Mean of the max with vocabulary {np.mean(matrix_max)}")
        self.logger.info(f"Mean with vabab vocabulary {np.mean(matrix_mean)}")

        return np.mean(matrix_max)


class Word2vecCallback(CallbackAny2Vec):
    """
    A callback class for logging the training loss after each epoch of a Word2Vec model.
    """

    def __init__(self):
        self.epoch = 0
        self.logger = logging.getLogger(__name__)

    def on_epoch_end(self, model):
        """
        Logs the training loss at the end of each epoch.
        """
        loss = model.get_latest_training_loss()
        self.logger.info(f"Loss after epoch {self.epoch} : {loss}")
        self.epoch += 1


def _rule(word, count, min_count):
    """
    A function to determine whether to keep a word in a Word2Vec vocabulary based on its frequency.

    Args:
        word (str): The word to check.
        count (int): The frequency of the word in the corpus.
        min_count (int): The minimum frequency threshold for keeping a word.

    Returns:
        int: One of the constants RULE_KEEP or RULE_DISCARD, depending on whether to keep or discard the word.
    """

    # useful for debugging and learning
    # pylint: disable=W0612,W0613
    # logger.info(f"_rule: {word}, {count}, {min_count}")
    return RULE_KEEP


def get_domain_keywords(vocabulary_file_path: str) -> list:
    """
    Reads a file containing a list of domain-specific keywords and returns them as a list.

    Args:
        vocabulary_file_path (str): The path to the file containing the domain-specific keywords.

    Returns:
        list: A list of domain-specific keywords.
    """

    vocabulary = []
    with smart_open.open(vocabulary_file_path, "r", encoding="utf-8") as file:
        for word in file.read().splitlines():
            vocabulary.append(word)

    return [vocabulary]


def load_word2vec_model(model_file_path: str) -> Word2Vec:
    """Loads a pre-trained Word2Vec model from a file and returns it.

    Args:
        model_file_path (str): The path to the Word2Vec model file to load.

    Returns:
        Word2Vec: The pre-trained Word2Vec model.

    Raises:
        PermissionError: If the user does not have the necessary permissions to read to the directory.
    """

    try:
        model = Word2Vec.load(model_file_path)
    except PermissionError:
        logger.error(
            f"Permission denied, check if you have the necessary permissions to read to the directory : \
            {os.path.dirname(model_file_path)}"
        )

    except FileNotFoundError:
        logger.error(
            f"The specified path does not exist, check if the path is correct : {os.path.dirname(model_file_path)}"
        )

    return model


def save_word2vec_model(model: Word2Vec, model_file_path: str):
    """
    Loads a pre-trained Word2Vec model from a file and returns it.

    Args:
        model_file_path (str): The path to the Word2Vec model file to load.

    Returns:
        Word2Vec: The pre-trained Word2Vec model.

    Raises:
        PermissionError: If the user does not have the necessary permissions to read the file.
        FileNotFoundError: If the file specified by `model_file_path` does not exist.
    """

    try:
        model.save(model_file_path)
    except PermissionError:
        logger.error(
            f"Permission denied, check if you have the necessary permissions to write to the directory : \
            {os.path.dirname(model_file_path)}"
        )

    except FileNotFoundError:
        logger.error(
            f"The specified path does not exist, check if the path is correct : {os.path.dirname(model_file_path)}"
        )


def save_word_embbeddings(word_vectors: KeyedVectors, word_vectors_file_path: str):
    """
    Saves a set of word embeddings to a file.

    Args:
        word_vectors (KeyedVectors): A set of word embeddings to save.
        word_vectors_file_path (str): The path to the file where the embeddings will be saved.

    Returns:
        None

    Raises:
        PermissionError: If the user does not have the necessary permissions to write to the file.
        FileNotFoundError: If the directory specified by `word_vectors_file_path` does not exist.
    """

    try:
        word_vectors.save(word_vectors_file_path)
    except PermissionError:
        logger.error(
            f"Permission denied, check if you have the necessary permissions to write to the directory : \
            {os.path.dirname(word_vectors_file_path)}"
        )

    except FileNotFoundError:
        logger.error(
            f"The specified path does not exist, check if the path is correct : \
            {os.path.dirname(word_vectors_file_path)}"
        )


def train_word2vec(sentences: list, vocabulary: list) -> tuple[Word2Vec, int, int]:
    """
    Trains a Word2Vec model on a set of sentences and vocabulary and returns the trained model and training statistics.

    Args:
        sentences (list): A list of sentences to train the Word2Vec model on.
        vocabulary (list): A list of domain-specific keywords to use as vocabulary for the Word2Vec model.

    Returns:
        tuple: A tuple containing the trained Word2Vec model, the number of words trained on, and the total number
        of words.

    Notes:
        Commonly used hyperparameters for training a word2vec model:

        size: The dimensionality of the word vectors. A common value is between 100 and 300.
        window: The maximum distance between the current and predicted word within a sentence. A common value is between
        5 and 10.
        min_count: The minimum frequency of a word in the corpus to be included in the vocabulary. A common value
        is between 5 and 10.
        workers: The number of threads to use for training. A common value is between 4 and 8, depending on the
        available hardware.
    """

    model = Word2Vec(
        callbacks=[Word2vecCallback()],
        compute_loss=True,
        vector_size=1000,
        window=5,
        min_count=4,
        workers=4,
    )

    model.build_vocab(
        corpus_iterable=vocabulary, min_count=1, progress_per=1, trim_rule=_rule
    )

    (trained_word_count, raw_word_count) = model.train(
        sentences,
        total_examples=model.corpus_count,
        epochs=10,
        report_delay=1.0,
        compute_loss=True,
        callbacks=[Word2vecCallback()],
    )

    return (model, trained_word_count, raw_word_count)


def evaluate_similarity(word_vectors: KeyedVectors, word1: str, word2: str) -> float:
    """
    Calculates the cosine similarity between two words in a set of word embeddings.

    Args:
        word_vectors (KeyedVectors): A set of word embeddings.
        word1 (str): The first word to compare.
        word2 (str): The second word to compare.

    Returns:
        float: The cosine similarity between the two words.
    """

    similarity = 0.0
    try:
        similarity = word_vectors.similarity(word1, word2)
    except KeyError:
        logger.warning("word not present")
    logger.info(
        f"The similarity between these two word {word1},{word2} is: {similarity}"
    )
    return similarity


def _is_mlflow_up():
    """
    Checks if MLflow is up and running.

    Returns:
        None
    """

    health_url = ""
    if "MLFLOW_TRACKING_URI" in os.environ:
        health_url = os.getenv("MLFLOW_TRACKING_URI")
    else:
        logger.error("MLFLOW_TRACKING_URI is not set.")

    try:
        response = requests.get(health_url + "/health", timeout=2)
        assert (
            response.status_code == 200
        ), f"Expected status code 200, but got {response.status_code} from MLflow server."

        assert (
            response.text == "OK"
        ), f"Expected response body 'OK', but got {response.text} from MLflow server."
    except ConnectionError:
        logger.error("Connection refused to the MLflow server.")
        sys.exit(1)


def train_and_track_experiment(model_uri: str, text_corpus: str, domain_keywords: str):
    """
    Trains a Word2Vec model on a text corpus using domain-specific keywords, and tracks the experiment with MLflow.

    Args:
        model_uri (str): The path to store the trained model artifact in MLflow.
        text_corpus (str): The path to the text corpus to train the Word2Vec model on.
        domain_keywords (str): The path to the file containing the domain-specific keywords to use as vocabulary
        for the model.

    Returns:
        str: The path to the trained model artifact in object storage.
    """

    _is_mlflow_up()
    mlflow.set_experiment("ppml_rr")

    with mlflow.start_run():
        vocabulary = get_domain_keywords(domain_keywords)
        corpus = get_file_contents(text_corpus)
        with_bigram_from_vocabulary = get_bigram_from_vocabulary(vocabulary, corpus)
        without_stopwords = clean_stopwords_str(with_bigram_from_vocabulary)
        text = get_bigram(without_stopwords)

        (model, trained_word_count, raw_word_count) = train_word2vec(text, vocabulary)

        with tempfile.NamedTemporaryFile(
            prefix="model_artifact_", delete=False
        ) as tmp_file:
            model_artifact_file_path = str(tmp_file.name)

        with tempfile.NamedTemporaryFile(
            prefix="word_embbeddings_", delete=False
        ) as tmp_file:
            word_embbeddings_file_path = str(tmp_file.name)

        save_word2vec_model(model, model_artifact_file_path)
        logger.info(f"Saving word2vec model into: {model_artifact_file_path}")
        save_word_embbeddings(model.wv, word_embbeddings_file_path)
        logger.info(f"Saving word embbeddings into: {word_embbeddings_file_path}")

        mlflow_model = GensimWord2VecModel(model, domain_keywords)

        mlflow.set_tag("python_version", platform.python_version())
        mlflow.set_tag("gensim_version", gensim.__version__)
        mlflow.set_tag("mlflow_version", mlflow.__version__)
        mlflow.log_param("vector_size", model.vector_size)
        mlflow.log_param("window", model.window)
        mlflow.log_param("min_count", model.min_count)
        mlflow.log_param("workers", model.workers)
        mlflow.log_param("trained_word_count", trained_word_count)
        mlflow.log_param("raw_word_count", raw_word_count)
        mlflow.log_artifact(domain_keywords, "domain_keywords")
        mlflow.log_artifact(text_corpus, "text_corpus")
        mlflow.log_artifact(word_embbeddings_file_path, "word_embbeddings/")
        mlflow.log_artifact(word_embbeddings_file_path, "model")

        mlflow.pyfunc.log_model(
            python_model=mlflow_model,
            artifact_path=model_uri,
            code_path=["./src"],
        )

        s3_full_path = mlflow.get_artifact_uri() + "/" + model_uri
        logger.info(f"MLflow model object-storage path: {s3_full_path}")
        return s3_full_path
