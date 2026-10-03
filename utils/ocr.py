import os
import shutil
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False


def find_tesseract_binary():
    """Locate tesseract binary on Windows or standard PATH."""
    # 1. Check system PATH
    which_path = shutil.which("tesseract")
    if which_path:
        return which_path

    # 2. Check standard Windows installation directories
    candidate_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        candidate_paths.append(str(Path(local_app_data) / "Programs" / "Tesseract-OCR" / "tesseract.exe"))

    for p in candidate_paths:
        if os.path.exists(p):
            return p
    return None


# Configure pytesseract path if found
TESSERACT_PATH = find_tesseract_binary()
if PYTESSERACT_AVAILABLE and TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def is_ocr_available() -> bool:
    """Return True if an OCR engine is available."""
    return PYTESSERACT_AVAILABLE and (TESSERACT_PATH is not None or shutil.which("tesseract") is not None)


def preprocess_image_for_ocr(img: Image.Image) -> Image.Image:
    """Enhance image for better OCR character recognition on lab reports."""
    # Convert to grayscale
    gray = img.convert("L")
    # Increase contrast
    enhancer = ImageEnhance.Contrast(gray)
    enhanced = enhancer.enhance(1.8)
    # Slight sharpening
    sharpened = enhanced.filter(ImageFilter.SHARPEN)
    return sharpened


def extract_text_from_image(image_input) -> dict:
    """
    Extract text from an image (filepath, PIL Image, or bytes).
    Returns dict: {'text': str, 'ocr_used': bool, 'error': str or None}
    """
    if not is_ocr_available():
        return {
            "text": "",
            "ocr_used": False,
            "error": "Tesseract OCR binary not found in system PATH. Digital PDF parsing is fully functional; for scanned images, please install Tesseract OCR.",
        }

    try:
        if isinstance(image_input, (str, Path)):
            img = Image.open(image_input)
        elif isinstance(image_input, Image.Image):
            img = image_input
        else:
            img = Image.open(image_input)

        processed_img = preprocess_image_for_ocr(img)
        text = pytesseract.image_to_string(processed_img, config="--psm 6")
        return {
            "text": text.strip(),
            "ocr_used": True,
            "error": None,
        }
    except Exception as exc:
        return {
            "text": "",
            "ocr_used": True,
            "error": f"OCR processing failed: {str(exc)}",
        }
