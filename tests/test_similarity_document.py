""" Test the similarity score. """
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("src"))

from ingestion.download import convert_pdf_to_text

# pylint: disable=C0413,W0012,W0611
from preparation.convert import get_file_contents
from training import (
    GensimWord2VecModel,
    load_word2vec_model,
)


class TestSimilarity(unittest.TestCase):
    """Test the similarity score."""

    def setUp(self):
        self.model_dir = os.path.join("tests", "data", "models")
        self.model = load_word2vec_model(os.path.join(self.model_dir, "small.model"))
        self.model = GensimWord2VecModel(
            self.model,
            "resources/keywords/keywords.txt",
        )
        self.tokens = ""
        self.tmp_path = (
            os.environ.get("TMPDIR")
            or os.environ.get("TEMP")
            or os.environ.get("RUNNER_TEMP")
        )

    def test_valid_2103_01035(self):
        """Test the similarity score."""
        convert_pdf_to_text("resources/benchmark/valid/2103.01035.pdf", self.tmp_path)
        self.tokens = get_file_contents(self.tmp_path + "2103.01035.txt")
        similarity_score = self.model.predict("", self.tokens)
        self.assertAlmostEqual(similarity_score, 0.725, places=2)

    def test_invalid_2208_11128(self):
        """Test the similarity score."""
        convert_pdf_to_text("resources/benchmark/invalid/2208.11128.pdf", self.tmp_path)
        self.tokens = get_file_contents(self.tmp_path + "2208.11128.txt")
        similarity_score = self.model.predict("", self.tokens)
        self.assertAlmostEqual(similarity_score, 0.994, places=2)

    def test_invalid_graham_2021_data_for_sale(self):
        """Test the similarity score."""
        convert_pdf_to_text(
            "resources/benchmark/invalid/graham_2021_data_for_sale.pdf", self.tmp_path
        )
        self.tokens = get_file_contents(self.tmp_path + "graham_2021_data_for_sale.txt")
        similarity_score = self.model.predict("", self.tokens)
        self.assertAlmostEqual(similarity_score, 0.995, places=2)

    def test_invalid_blank(self):
        """Test the similarity score."""
        convert_pdf_to_text("resources/benchmark/invalid/blank.pdf", self.tmp_path)
        self.tokens = get_file_contents(self.tmp_path + "blank.txt")
        similarity_score = self.model.predict("", self.tokens)
        self.assertAlmostEqual(similarity_score, 0.0, places=2)
