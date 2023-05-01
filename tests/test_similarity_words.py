""" Test the similarity of words. """
import os
import unittest
import logging
import sys

sys.path.insert(0, os.path.abspath("src"))

# pylint: disable=C0413,W0012,W0611
from training import (
    GensimWord2VecModel,
    evaluate_similarity,
    load_word2vec_model,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TestWords(unittest.TestCase):
    def setUp(self):
        domain_keywords_path = ""
        if "DOMAIN_KEYWORDS" in os.environ:
            domain_keywords_path = os.environ["DOMAIN_KEYWORDS"]
        else:
            logger.info("The DOMAIN_KEYWORDS environment variable does not exist.")

        self.model_dir = os.path.join("tests", "data", "models")
        self.model = load_word2vec_model(os.path.join(self.model_dir, "small.model"))
        self.model = GensimWord2VecModel(
            self.model,
            domain_keywords_path,
        )
        self.tokens = ""

    def test_causal_sem(self):
        """Test the similarity score."""
        similarity_score = evaluate_similarity(
            self.model.word2vec_model.wv, "causal", "sem"
        )
        self.assertAlmostEqual(similarity_score, 0.030, places=2)

    def test_stratified_stratification(self):
        """Test the similarity score."""
        similarity_score = evaluate_similarity(
            self.model.word2vec_model.wv, "stratified", "stratification"
        )
        self.assertAlmostEqual(similarity_score, 0.005, places=2)

    def test_causal_hierarchy_causal_hierarchy(self):
        """Test the similarity score."""
        similarity_score = evaluate_similarity(
            self.model.word2vec_model.wv, "causal_hierarchy", "causal_hierarchy"
        )
        self.assertAlmostEqual(similarity_score, 1.0, places=2)

    def test_causal_hierarchy_sem(self):
        """Test the similarity score."""
        similarity_score = evaluate_similarity(
            self.model.word2vec_model.wv, "causal_hierarchy", "sem"
        )
        self.assertAlmostEqual(similarity_score, -0.014, places=2)

    def test_sem_stratified(self):
        """Test the similarity score."""
        similarity_score = evaluate_similarity(
            self.model.word2vec_model.wv, "sem", "stratified"
        )
        self.assertAlmostEqual(similarity_score, 0.049, places=2)

    def test_experimental_observational(self):
        """Test the similarity score."""
        similarity_score = evaluate_similarity(
            self.model.word2vec_model.wv, "experimental", "observational"
        )
        self.assertAlmostEqual(similarity_score, 0.102, places=2)

    def test_backdoor_do_calculus(self):
        """Test the similarity score."""
        similarity_score = evaluate_similarity(
            self.model.word2vec_model.wv, "backdoor", "do_calculus"
        )
        self.assertAlmostEqual(similarity_score, 0.010, places=2)

    def test_latent_confounding(self):
        """Test the similarity score."""
        similarity_score = evaluate_similarity(
            self.model.word2vec_model.wv, "latent", "confounding"
        )
        self.assertAlmostEqual(similarity_score, -0.021, places=2)

    def test_latent_unobserved_confounder(self):
        """Test the similarity score."""
        similarity_score = evaluate_similarity(
            self.model.word2vec_model.wv, "latent", "unobserved_confounder"
        )
        self.assertAlmostEqual(similarity_score, -0.000, places=2)
