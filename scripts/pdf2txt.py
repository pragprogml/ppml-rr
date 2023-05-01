#!/usr/bin/env python3

"""Converts a PDF file to a clean plain text file."""

import argparse
import os
import sys

sys.path.insert(0, os.path.abspath("src"))

from ingestion.download import convert_pdf_to_text

parser = argparse.ArgumentParser(
    description="Convert a PDF file to a clean plain text file."
)

parser.add_argument(
    "-f", "--pdf-file", dest="pdf_file", required=True, help="Pdf input file"
)

parser.add_argument(
    "-d",
    "--destination",
    required=True,
    help="TXT out directory",
)

args = parser.parse_args()

pdf_file = args.pdf_file
destination = args.destination

convert_pdf_to_text(pdf_file, destination)
