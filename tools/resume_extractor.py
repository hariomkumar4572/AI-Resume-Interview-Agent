import io
import os
from typing import Union, BinaryIO, Optional
import pymupdf  # PyMuPDF
import fitz    # Alias for PyMuPDF compatibility
import docx

# Magic byte signatures
PDF_MAGIC_BYTES = b"%PDF"
ZIP_MAGIC_BYTES = b"PK\x03\x04"  # DOCX is a zip container containing word/document.xml


def detect_file_signature(data: bytes) -> str:
    """
    Detects whether binary data matches PDF or DOCX file signatures.
    """
    if len(data) >= 4 and data.startswith(PDF_MAGIC_BYTES):
        return "pdf"
    if len(data) >= 4 and data.startswith(ZIP_MAGIC_BYTES):
        return "docx"
    return "unknown"


def extract_resume_from_pdf(source: Union[str, bytes, BinaryIO]) -> str:
    """
    Extracts text from a PDF file using PyMuPDF (fitz.open).
    Accepts a file path, raw bytes, or a file-like stream (such as UploadedFile).
    Handles empty, encrypted, and corrupted PDFs with descriptive errors.
    """
    doc = None
    try:
        if isinstance(source, bytes):
            pdf_bytes = source
        elif hasattr(source, "getvalue"):  # e.g., Streamlit UploadedFile
            pdf_bytes = source.getvalue()
        elif hasattr(source, "read"):  # Generic file-like object
            pos = source.tell() if hasattr(source, "tell") else 0
            if hasattr(source, "seek"):
                source.seek(0)
            pdf_bytes = source.read()
            if hasattr(source, "seek"):
                source.seek(pos)
        elif isinstance(source, str):
            if not os.path.exists(source):
                raise FileNotFoundError(f"PDF file not found at path: {source}")
            with open(source, "rb") as f:
                pdf_bytes = f.read()
        else:
            raise ValueError(f"Unsupported source type for PDF: {type(source).__name__}")

        if not pdf_bytes or len(pdf_bytes.strip()) == 0:
            raise ValueError("The provided PDF file is completely empty (0 bytes).")

        # Verify PDF signature (%PDF)
        if not pdf_bytes.startswith(PDF_MAGIC_BYTES):
            # Check if %PDF appears within the first 1024 bytes (some PDF generators leave header space)
            if PDF_MAGIC_BYTES not in pdf_bytes[:1024]:
                raise ValueError("File header does not match valid PDF specification (missing %PDF signature).")

        # Open PDF from bytes using fitz.open(stream=pdf_bytes, filetype="pdf")
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as open_err:
            raise ValueError(f"Corrupted or malformed PDF file: {str(open_err)}") from open_err

        # Check encryption / password protection
        if doc.is_encrypted:
            # Try decrypting with blank password
            if not doc.authenticate(""):
                raise ValueError("The PDF resume is password-protected or encrypted. Please upload an unencrypted document.")

        if doc.page_count == 0:
            raise ValueError("The PDF document contains 0 pages.")

        text_parts = []
        for page_num in range(doc.page_count):
            page = doc[page_num]
            page_text = page.get_text()
            if page_text:
                text_parts.append(page_text.strip())

        extracted = "\n\n".join(text_parts).strip()
        if not extracted:
            raise ValueError(
                "The PDF document contains no readable text. It may be a scanned image or bitmap. "
                "Please upload a text-based PDF or DOCX resume."
            )

        return extracted
    except (ValueError, FileNotFoundError):
        raise
    except Exception as e:
        raise RuntimeError(f"Unexpected error extracting PDF: {str(e)}") from e
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass


def extract_resume_from_docx(source: Union[str, bytes, BinaryIO]) -> str:
    """
    Extracts text from a DOCX file using python-docx and io.BytesIO.
    Accepts a file path, raw bytes, or a file-like stream (such as UploadedFile).
    Handles empty, invalid, and corrupted DOCX files.
    """
    try:
        if isinstance(source, bytes):
            docx_bytes = source
        elif hasattr(source, "getvalue"):  # e.g., Streamlit UploadedFile
            docx_bytes = source.getvalue()
        elif hasattr(source, "read"):
            pos = source.tell() if hasattr(source, "tell") else 0
            if hasattr(source, "seek"):
                source.seek(0)
            docx_bytes = source.read()
            if hasattr(source, "seek"):
                source.seek(pos)
        elif isinstance(source, str):
            if not os.path.exists(source):
                raise FileNotFoundError(f"DOCX file not found at path: {source}")
            with open(source, "rb") as f:
                docx_bytes = f.read()
        else:
            raise ValueError(f"Unsupported source type for DOCX: {type(source).__name__}")

        if not docx_bytes or len(docx_bytes.strip()) == 0:
            raise ValueError("The provided DOCX file is completely empty (0 bytes).")

        # Verify ZIP signature (PK\x03\x04)
        if not docx_bytes.startswith(ZIP_MAGIC_BYTES):
            raise ValueError("File header does not match valid DOCX specification (missing PK zip signature).")

        # Open DOCX using io.BytesIO
        stream = io.BytesIO(docx_bytes)
        try:
            doc = docx.Document(stream)
        except Exception as docx_err:
            raise ValueError(f"Corrupted or invalid DOCX archive: {str(docx_err)}") from docx_err

        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

        table_texts = []
        for table in doc.tables:
            for row in table.rows:
                row_str = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_str:
                    table_texts.append(row_str)

        all_content = paragraphs + table_texts
        extracted = "\n".join(all_content).strip()

        if not extracted:
            raise ValueError("The DOCX document contains no readable text content.")

        return extracted
    except (ValueError, FileNotFoundError):
        raise
    except Exception as e:
        raise RuntimeError(f"Unexpected error extracting DOCX: {str(e)}") from e


def extract_resume(file_path_or_content: Union[str, bytes, BinaryIO], file_type: str = "") -> str:
    """
    Tool 1: extract_resume
    Extract and return readable resume text from PDF or DOCX format, or raw text strings.
    Validates file format, MIME/extension signatures, and handles empty, encrypted,
    or corrupted documents with clear error feedback.
    """
    if file_path_or_content is None:
        raise ValueError("No resume content provided. Please upload a file.")

    # Check if raw text was passed (e.g. from a prior extraction or string source)
    if isinstance(file_path_or_content, str):
        # If it's a file path on disk
        if (
            file_path_or_content.lower().endswith(".pdf")
            or file_path_or_content.lower().endswith(".docx")
            or os.path.exists(file_path_or_content)
        ):
            if os.path.isfile(file_path_or_content):
                target_type = file_type.lower().strip()
                if not target_type:
                    if file_path_or_content.lower().endswith(".pdf"):
                        target_type = "pdf"
                    elif file_path_or_content.lower().endswith(".docx"):
                        target_type = "docx"
                if target_type == "pdf":
                    return extract_resume_from_pdf(file_path_or_content)
                elif target_type == "docx":
                    return extract_resume_from_docx(file_path_or_content)
                else:
                    # Sniff signature from file
                    with open(file_path_or_content, "rb") as f:
                        header = f.read(8)
                    sig = detect_file_signature(header)
                    if sig == "pdf":
                        return extract_resume_from_pdf(file_path_or_content)
                    elif sig == "docx":
                        return extract_resume_from_docx(file_path_or_content)
                    raise ValueError(f"Unsupported file format for path: {file_path_or_content}")
        # Otherwise, the string is already extracted resume text
        if file_type.lower() == "text" or len(file_path_or_content.splitlines()) > 1 or " " in file_path_or_content:
            if not file_path_or_content.strip():
                raise ValueError("Resume text is empty.")
            return file_path_or_content.strip()

    # Obtain bytes to inspect signature
    data_bytes = None
    if isinstance(file_path_or_content, bytes):
        data_bytes = file_path_or_content
    elif hasattr(file_path_or_content, "getvalue"):  # Streamlit UploadedFile
        data_bytes = file_path_or_content.getvalue()
    elif hasattr(file_path_or_content, "read"):
        pos = file_path_or_content.tell() if hasattr(file_path_or_content, "tell") else 0
        if hasattr(file_path_or_content, "seek"):
            file_path_or_content.seek(0)
        data_bytes = file_path_or_content.read()
        if hasattr(file_path_or_content, "seek"):
            file_path_or_content.seek(pos)

    if data_bytes is None or len(data_bytes.strip()) == 0:
        raise ValueError("Resume file appears to be empty or contains 0 bytes.")

    # Determine file type via explicit type, file signature, or extension
    target_type = file_type.lower().strip()
    if not target_type or target_type == "unknown":
        sig = detect_file_signature(data_bytes)
        if sig in ("pdf", "docx"):
            target_type = sig
        elif hasattr(file_path_or_content, "name"):
            fname = str(file_path_or_content.name).lower()
            if fname.endswith(".pdf"):
                target_type = "pdf"
            elif fname.endswith(".docx"):
                target_type = "docx"

    # Process extraction
    if target_type == "pdf":
        return extract_resume_from_pdf(data_bytes)
    elif target_type == "docx":
        return extract_resume_from_docx(data_bytes)
    else:
        # Fallback inspection: attempt PDF first, then DOCX
        pdf_error = None
        try:
            return extract_resume_from_pdf(data_bytes)
        except Exception as e:
            pdf_error = e

        docx_error = None
        try:
            return extract_resume_from_docx(data_bytes)
        except Exception as e:
            docx_error = e

        raise ValueError(
            f"Unsupported or corrupt file format. Please provide a valid PDF or DOCX file.\n"
            f"(PDF check: {pdf_error}; DOCX check: {docx_error})"
        )
