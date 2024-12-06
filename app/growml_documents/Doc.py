import os
import subprocess
import tempfile
from io import BytesIO
from pathlib import Path

from growml_documents.Document import Document
from growml_documents.Docx import Docx


class Doc(Document):
    def __init__(self, filepath_or_buffer: str | Path | BytesIO):
        super().__init__(filepath_or_buffer)
        self.docx_path = self.convert_doc_to_docx()
        self.docx = Docx(self.docx_path)

    def convert_doc_to_docx(self):
        temp_dir = tempfile.mkdtemp()
        output_filename = os.path.basename(self.file_path).rsplit(".", 1)[0] + ".docx"
        subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                "docx",
                self.file_path,
                "--outdir",
                temp_dir,
            ]
        )
        docx_path = os.path.join(temp_dir, output_filename)
        return docx_path

    def read_text(self):
        return self.docx.read_text()

    def read_from_metadata(self):
        return self.read_text()

    def count_pages(self):
        return self.docx.count_pages()

    def get_paragraphs(self):
        return self.docx.get_paragraphs()

    def get_tables(self):
        return self.docx.get_tables()

    def __del__(self):
        os.unlink(self.docx_path)
