"""Module for cleaning, n-gramming and text conversion."""

import logging

from .clean import *
from .convert import *

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
