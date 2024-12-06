import subprocess
from multiprocessing import Pool


class OCR:
    def __init__(self, n_parallel=1):
        self.n_parallel = n_parallel

    def run_tesseract(self, image_path, lang="spa"):
        command = ["tesseract", image_path, "stdout", "-l", lang]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        text = result.stdout
        return text

    def read_images(self, images_paths):
        with Pool(processes=self.n_parallel) as pool:
            texts = pool.map(self.run_tesseract, images_paths)
        doc_text = " ".join(texts)
        return doc_text
