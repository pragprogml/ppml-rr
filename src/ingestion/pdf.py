"""Pdf validation and conversion module."""

import hashlib
import logging
from pathlib import Path

import smart_open
from pypdf import PdfReader
from pypdf.errors import PdfReadError


class Pdf:
    """
    Represents a PDF file and provides methods for validation and conversion to text.
    """

    path: str
    """path (str): The path to the PDF file."""
    filename: str
    """filename (str): The name of the PDF file."""
    hash: str
    """hash (str): The SHA-256 hash of the PDF file content."""
    content: str
    """content (str): The text content of the PDF file."""
    number_of_pages: int
    """number_of_pages (int): The number of pages in the PDF file."""

    def __init__(self, path):
        self.path = path
        self.logger = logging.getLogger(__name__)

    def to_text(self):
        """
        Convert the PDF to text and store the text content in the content attribute.
        """
        self.content = ""
        with smart_open.open(self.path, "rb") as filehandle:
            file_content = filehandle.read()

            self.hash = hashlib.sha256(file_content).hexdigest()
            self.filename = Path(self.path).stem
            self.content = ""

            try:
                pdf_file_obj = PdfReader(filehandle, strict=True)
            except OSError:
                self.logger.error(f"The PDF file may be corrupt: {self.filename}.pdf")

            except PdfReadError:
                self.logger.error(f"The PDF file may be corrupt: {self.filename}.pdf ")

            else:
                self.number_of_pages = len(pdf_file_obj.pages)
                self.logger.info(
                    f"{self.filename}.pdf contains {self.number_of_pages} pages"
                )
                for i in range(self.number_of_pages):
                    page = pdf_file_obj.pages[i]
                    self.content += page.extract_text()

    def save(self, destination_path: str):
        """
        Save the text content of the PDF file to a text file in the given destination directory.
        """
        txt_file_path = destination_path + self.filename + ".txt"
        self.logger.info(f"Saving text to file: {txt_file_path}")

        with smart_open.open(txt_file_path, "w", encoding="utf-8") as filehandle:
            filehandle.write(self.content)
