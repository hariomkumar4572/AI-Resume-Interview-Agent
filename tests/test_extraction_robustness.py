import io
import os
import unittest
import pymupdf
import docx

from tools.resume_extractor import (
    extract_resume,
    extract_resume_from_pdf,
    extract_resume_from_docx,
    detect_file_signature,
)

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "samples")


class MockUploadedFile:
    """Simulates Streamlit's UploadedFile object with consumed read() and getvalue()."""
    def __init__(self, name: str, data: bytes):
        self.name = name
        self._data = data
        self._stream = io.BytesIO(data)
        # Simulate consumed pointer as often happens in Streamlit
        self._stream.read()

    def getvalue(self) -> bytes:
        return self._data

    def read(self, *args, **kwargs) -> bytes:
        return self._stream.read(*args, **kwargs)

    def seek(self, *args, **kwargs):
        return self._stream.seek(*args, **kwargs)

    def tell(self) -> int:
        return self._stream.tell()


class TestResumeExtractionRobustness(unittest.TestCase):
    def test_streamlit_uploaded_file_consumed_stream(self):
        """Verify that an UploadedFile whose read() pointer is at EOF still extracts perfectly via getvalue()."""
        pdf_path = os.path.join(SAMPLES_DIR, "python_developer.pdf")
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        mock_file = MockUploadedFile("python_developer.pdf", pdf_bytes)
        # Confirm that read() without seek would return empty
        self.assertEqual(mock_file.read(), b"")

        # extract_resume must handle it using getvalue()
        extracted = extract_resume(mock_file, file_type="pdf")
        self.assertIn("Aarav Sharma", extracted)
        self.assertIn("FastAPI", extracted)

    def test_streamlit_uploaded_file_docx(self):
        docx_path = os.path.join(SAMPLES_DIR, "python_developer.docx")
        with open(docx_path, "rb") as f:
            docx_bytes = f.read()

        mock_file = MockUploadedFile("python_developer.docx", docx_bytes)
        extracted = extract_resume(mock_file, file_type="docx")
        self.assertIn("Aarav Sharma", extracted)

    def test_pdf_bytes_direct_extraction(self):
        pdf_path = os.path.join(SAMPLES_DIR, "ai_ml_engineer.pdf")
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        extracted = extract_resume(pdf_bytes, file_type="pdf")
        self.assertIn("Vikram Sen", extracted)
        self.assertIn("PyTorch", extracted)

    def test_empty_file_handling(self):
        with self.assertRaises(ValueError) as ctx:
            extract_resume(b"", file_type="pdf")
        self.assertIn("empty", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx:
            extract_resume(MockUploadedFile("empty.pdf", b""))
        self.assertIn("empty", str(ctx.exception).lower())

    def test_corrupt_file_handling(self):
        corrupt_bytes = b"Not a real PDF or DOCX file content"
        with self.assertRaises(ValueError) as ctx:
            extract_resume(corrupt_bytes, file_type="pdf")
        self.assertTrue("signature" in str(ctx.exception).lower() or "pdf specification" in str(ctx.exception).lower())

    def test_encrypted_pdf_detection(self):
        # Create an in-memory encrypted PDF to verify password-protection handling
        doc = pymupdf.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Secret Resume Text")
        perm = int(
            pymupdf.PDF_PERM_ACCESSIBILITY
            | pymupdf.PDF_PERM_PRINT
            | pymupdf.PDF_PERM_COPY
            | pymupdf.PDF_PERM_ANNOTATE
        )
        encrypted_bytes = doc.tobytes(
            encryption=pymupdf.PDF_ENCRYPT_AES_256,
            owner_pw="secret_owner",
            user_pw="secret_user",
            permissions=perm,
        )
        doc.close()

        with self.assertRaises(ValueError) as ctx:
            extract_resume(encrypted_bytes, file_type="pdf")
        self.assertIn("password", str(ctx.exception).lower())

    def test_multiple_valid_sample_pdfs(self):
        sample_names = [
            ("python_developer.pdf", "Aarav Sharma"),
            ("java_developer.pdf", "Priya Patel"),
            ("web_developer.pdf", "Rohan Verma"),
            ("data_analyst.pdf", "Neha Kulkarni"),
            ("ai_ml_engineer.pdf", "Vikram Sen"),
            ("fresher_no_experience.pdf", "Sneha Reddy"),
        ]
        for fname, expected_name in sample_names:
            fpath = os.path.join(SAMPLES_DIR, fname)
            extracted = extract_resume(fpath)
            self.assertIn(expected_name, extracted, f"Failed for sample {fname}")


if __name__ == "__main__":
    unittest.main()
