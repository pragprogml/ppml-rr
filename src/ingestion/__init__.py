"""Module for arXiv article download and pdf processing."""

import logging

from .arxiv_client import *
from .pdf import *
from .download import *

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
