from growml_documents.Doc import Doc
from growml_documents.Docx import Docx
from growml_documents.PDF import PDF


class TextReader:
    def __init__(self, file_path, n_parallel=1):
        self.file_path = file_path
        self.n_parallel = n_parallel
        self.doc = self.init_document()

    def init_document(self):
        if str(self.file_path).endswith(".pdf"):
            return PDF(self.file_path, n_parallel=self.n_parallel)
        elif str(self.file_path).endswith(".docx"):
            return Docx(self.file_path)
        elif str(self.file_path).endswith(".doc"):
            return Doc(self.file_path)

    def read_text(self):
        return self.doc.read_text()


def read_text(file_path, n_parallel=1):
    return TextReader(file_path, n_parallel).read_text()
