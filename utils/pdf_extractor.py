import io
import os
from pathlib import Path
from PIL import Image

try:
    import pymupdf as fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    try:
        import fitz
        PYMUPDF_AVAILABLE = True
    except ImportError:
        PYMUPDF_AVAILABLE = False


try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

from utils.ocr import extract_text_from_image, is_ocr_available


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}


def normalize_extracted_text(text: str) -> str:
    """
    Normalize extracted document text.
    Handles:
    - Custom diagnostic font encodings mapped to Unicode Private Use Area (0xF000-0xF0FF)
      converting them to standard ASCII characters (0x00-0xFF).
    - Non-breaking spaces and zero-width characters.
    """
    if not text:
        return ""
    
    chars = []
    for ch in text:
        code = ord(ch)
        if 0xF020 <= code <= 0xF0FF:
            chars.append(chr(code - 0xF000))
        elif 0xF000 <= code <= 0xF01F:
            chars.append(" ")
        elif ch in {"\u00a0", "\u2000", "\u2001", "\u2002", "\u2003", "\u2009", "\u202f"}:
            chars.append(" ")
        else:
            chars.append(ch)
    
    return "".join(chars).strip()


def extract_document_content(file_path: str | Path) -> dict:
    """
    Unified extractor for medical reports.
    Accepts digital PDF, scanned PDF, or medical report image.
    Returns:
        {
            "text": str,
            "doc_type": "text_pdf" | "scanned_pdf" | "image",
            "ocr_used": bool,
            "num_pages": int,
            "file_name": str,
            "file_size_kb": float,
            "warnings": list,
        }
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    file_ext = path.suffix.lower()
    file_size_kb = round(path.stat().st_size / 1024, 2)
    file_name = path.name
    warnings = []

    # 1. Handle Direct Image Uploads
    if file_ext in IMAGE_EXTENSIONS:
        ocr_result = extract_text_from_image(path)
        if ocr_result["error"]:
            warnings.append(ocr_result["error"])
        return {
            "text": ocr_result["text"],
            "doc_type": "image",
            "ocr_used": True,
            "num_pages": 1,
            "file_name": file_name,
            "file_size_kb": file_size_kb,
            "warnings": warnings,
        }

    # 2. Handle PDF Uploads
    if file_ext == ".pdf":
        extracted_text = ""
        is_scanned = False
        num_pages = 0

        # Method A: Try pdfplumber first (best for tables and layout)
        if PDFPLUMBER_AVAILABLE:
            try:
                with pdfplumber.open(str(path)) as pdf:
                    num_pages = len(pdf.pages)
                    plumb_texts = []
                    for page in pdf.pages:
                        pt = page.extract_text(layout=True) or ""
                        # Also check tables in lab reports
                        tables = page.extract_tables() or []
                        table_str = "\n".join([" | ".join([str(c) for c in row if c]) for table in tables for row in table])
                        combined = f"{pt}\n{table_str}".strip()
                        plumb_texts.append(combined)
                    extracted_text = "\n\n".join(plumb_texts)
            except Exception as e:
                warnings.append(f"pdfplumber parsing error: {str(e)}")

        # Method B: Fallback to PyMuPDF if text is empty or likely scanned
        if (not extracted_text.strip() or len(extracted_text) < 40 * max(1, num_pages)) and PYMUPDF_AVAILABLE:
            try:
                doc = fitz.open(str(path))
                num_pages = max(num_pages, len(doc))
                page_texts = []
                for page_idx in range(len(doc)):
                    page = doc[page_idx]
                    p_text = page.get_text("text").strip()
                    page_texts.append(p_text)

                total_chars = sum(len(pt) for pt in page_texts)
                if total_chars < 40 * max(1, len(doc)):
                    is_scanned = True
                    warnings.append("Document appears to be a scanned or image-based PDF. Attempting OCR.")
                    # OCR page by page
                    ocr_pages = []
                    for page_idx in range(min(len(doc), 5)):  # Process up to first 5 pages for efficiency
                        page = doc[page_idx]
                        pix = page.get_pixmap(dpi=200)
                        img = Image.open(io.BytesIO(pix.tobytes("png")))
                        ocr_res = extract_text_from_image(img)
                        if ocr_res["error"]:
                            warnings.append(f"Page {page_idx + 1} OCR note: {ocr_res['error']}")
                        ocr_pages.append(ocr_res["text"])
                    extracted_text = "\n\n".join(ocr_pages)
                else:
                    # PyMuPDF found text but pdfplumber failed
                    extracted_text = "\n\n".join(page_texts)

                doc.close()
            except Exception as e:
                warnings.append(f"PyMuPDF parsing error: {str(e)}")


        doc_type = "scanned_pdf" if is_scanned else "text_pdf"
        normalized_final_text = normalize_extracted_text(extracted_text)
        return {
            "text": normalized_final_text,
            "doc_type": doc_type,
            "ocr_used": is_scanned,
            "num_pages": num_pages,
            "file_name": file_name,
            "file_size_kb": file_size_kb,
            "warnings": warnings,
        }

    raise ValueError(f"Unsupported file format: {file_ext}. Please upload a PDF or medical report image (PNG, JPG).")
