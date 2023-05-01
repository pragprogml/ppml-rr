"""Module for generating embeddings and model training."""

import logging
import sys

from .training import *

sys.path.append("src")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
