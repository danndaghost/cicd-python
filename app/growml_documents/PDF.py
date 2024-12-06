import os
import shutil
import subprocess
from io import BytesIO
from pathlib import Path

import pymupdf

from growml_documents.Document import Document
from growml_documents.OCR import OCR


class PDF(Document):
    file_path: str | Path
    doc: pymupdf.Document
    num_pages: int

    def __init__(self, filepath_or_buffer: str | Path | BytesIO, n_parallel=1):
        super().__init__(filepath_or_buffer)
        self.n_parallel = n_parallel
        self.doc = pymupdf.open(self.file_path)
        self.has_text = bool(self.doc.load_page(0).get_text())
        self.num_pages = self.doc.page_count
        self.ocr_threshold = 10

    def pdf_to_images(self):
        self.run_split_pdf()
        folder_path = self.run_parallel_pdf_to_image()
        image_paths = [folder_path / f"{i+1}-1.png" for i in range(self.num_pages)]
        return image_paths

    def run_parallel_pdf_to_image(self):
        path = self.file_path.parent / self.file_path.stem
        command = (
            f"cd {path} && "
            "parallel mutool convert -o {/.}-%01d.png -F png {} ::: *.pdf"
        )
        subprocess.run(command, shell=True, check=True)
        return path

    def run_split_pdf(self):
        # Construct the Tesseract command
        path = self.file_path.parent / self.file_path.stem
        os.makedirs(path, exist_ok=True)
        command = ["pdftk", self.file_path, "burst", "output", f"{path}/%d.pdf"]

        # Run the command and capture the output
        subprocess.run(command, capture_output=True, text=True, check=True)

    def read_text(self):
        if self.has_text and self.count_words_per_page() > self.ocr_threshold:
            pages_text = self.read_from_metadata()
            text = " ".join(pages_text)
        else:
            text = self.read_from_ocr()
        return text

    def count_pages(self):
        return self.num_pages

    def read_from_metadata(self) -> list[str]:
        pages = [self.doc.load_page(idx) for idx in range(self.num_pages)]
        return " ".join([page.get_text() for page in pages])

    def read_from_ocr(self):
        images_paths = self.pdf_to_images()
        doc_text = OCR(n_parallel=self.n_parallel).read_images(images_paths)
        shutil.rmtree(images_paths[0].parent)
        return doc_text
