#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Test the similarity of words. """
import os
import unittest
import logging
import sys

sys.path.insert(0, os.path.abspath("src"))

from ingestion.download import Pdf
from preparation.clean import (
    combined_text_cleaning,
    clean_stopwords_str,
    get_bigram_from_vocabulary,
)
from training import get_domain_keywords

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TestConversion(unittest.TestCase):
    """Test the similarity of words."""

    def setUp(self):
        self.text = "In recent years, as AI systems are increasingly deployed in \
everyday life, there has been a slew of research papers on the \
problem of eXplainable AI (XAI), driven by concerns about \
whether these systems are fair, accountable and trustworthy. \
In the literature on post-hoc explanations, that aim to justify \
an AI model’s predictions after the fact, the usefulness of \
giving counterfactual explanations has gained considerable \
traction based on claimed technical, psychological and legal \
benefits (see Figure 1). Counterfactual explanations provide \
information to users on what might be done to change the \
outcome of an automated decision (e.g., “if your paper had \
more novelty, it would have been accepted to this \
conference”). In this paper, we critically review the \
evaluations carried out on counterfactual explanation \
methods, focusing on psychological issues. To put it simply, \
we assess whether there is any evidence that counterfactuals \
explanations “work” and/or whether the properties \
promulgated in current methods are relevant to end users. So, \
this review is, in part, a critique on the paucity of user testing"

    def test_clean_stopwords_string(self):
        text = clean_stopwords_str(self.text)
        self.assertEqual(len(text[0]), 87)

    def test_combined_text_cleaning(self):
        text = combined_text_cleaning(self.text)
        self.assertEqual(len(text), 740)

    def test_get_bigram_from_vocabulary(self):
        vocabulary = get_domain_keywords("resources/keywords/keywords.txt")
        self.text = combined_text_cleaning(self.text)
        self.text = get_bigram_from_vocabulary(vocabulary, self.text)
        bigram_count = 0
        for word in self.text.split():
            bigram_count += word.count("_")
        self.assertEqual(bigram_count, 3)

    def test_pdf_to_text(self):
        """Test the similarity score."""
        pdf_file = Pdf("resources/benchmark/valid/2103.01035.pdf")
        pdf_file.to_text()
        pdf_file.content = combined_text_cleaning(pdf_file.content)

        self.assertEqual(len(pdf_file.content.split()), 5441)
        assert "government" in pdf_file.content
        assert "focusing" in pdf_file.content
        assert "explanation" in pdf_file.content
        assert "multiagent" in pdf_file.content
        assert "superpixels" in pdf_file.content
