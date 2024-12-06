import os
import tempfile
from io import BytesIO
from pathlib import Path

import gcsfs


class Document:
    def __init__(self, filepath_or_buffer: str | Path | BytesIO):
        self.is_temp_file = False

        if isinstance(filepath_or_buffer, BytesIO):
            self.is_temp_file = True
            with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as temp_file:
                temp_file.write(filepath_or_buffer.getvalue())
                file_path = Path(temp_file.name)
        elif isinstance(filepath_or_buffer, (str, Path)):
            filepath_or_buffer = str(filepath_or_buffer)

            if filepath_or_buffer.startswith("gs://"):
                if self._gcs_file_exists(filepath_or_buffer):
                    file_path = self._read_from_gcs(filepath_or_buffer)
                    self.is_temp_file = True
                else:
                    raise FileNotFoundError(
                        f"The file at {filepath_or_buffer} does not exist."
                    )
            else:
                file_path = Path(filepath_or_buffer)
                if not file_path.exists():
                    raise FileNotFoundError(f"The file at {file_path} does not exist.")
        else:
            raise ValueError("Invalid source type. Must be str, Path, or BytesIO.")

        self.file_path = file_path

    def count_pages(self):
        raise NotImplementedError

    def read_from_metadata(self):
        raise NotImplementedError

    def count_words(self):
        text = self.read_from_metadata()
        words = text.split()
        return len(words)

    def count_words_per_page(self):
        return self.count_words() / self.count_pages()

    def _read_from_gcs(self, gcs_path: str) -> Path:
        """
        Read a file from Google Cloud Storage and save it to a temporary local file.
        Returns the path to the temporary file.
        """
        fs = gcsfs.GCSFileSystem()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as temp_file:
            with fs.open(gcs_path, "rb") as gcs_file:
                temp_file.write(gcs_file.read())
        return Path(temp_file.name)

    def _gcs_file_exists(self, gcs_path: str) -> bool:
        """
        Check if a file exists in Google Cloud Storage.
        """
        fs = gcsfs.GCSFileSystem()
        return fs.exists(gcs_path)

    def __del__(self):
        if self.is_temp_file and hasattr(self, "file_path"):
            try:
                os.unlink(self.file_path)
            except OSError:
                pass
