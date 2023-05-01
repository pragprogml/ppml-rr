"""Module for profiling python code."""

import logging

from .profiling import *

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
