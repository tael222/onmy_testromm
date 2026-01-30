"""OCR module for ReadAlongBuddy - text recognition from book images."""

import os
import platform
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract

# Optional: OpenCV for advanced preprocessing
try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

if platform.system() == "Windows":
    _tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(_tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = _tesseract_path

# Language mapping for OCR
LANG_MAP = {
    "영어": "eng",
    "한글": "kor",
    "영어+한글": "eng+kor",
}


def preprocess_image_basic(image: Image.Image) -> Image.Image:
    """Basic preprocessing using PIL only."""
    img = image.convert("L")
    # Upscale small images for better OCR
    w, h = img.size
    if w < 1500:
        scale = 1500 / w
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.8)
    # Sharpen
    img = img.filter(ImageFilter.SHARPEN)
    img = img.filter(ImageFilter.SHARPEN)
    # Auto-contrast to normalize brightness
    img = ImageOps.autocontrast(img, cutoff=2)
    return img


def preprocess_image_advanced(image: Image.Image) -> Image.Image:
    """Advanced preprocessing using OpenCV for blurry/low-quality images."""
    # Convert PIL to OpenCV format
    img_array = np.array(image.convert("RGB"))
    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

    # Convert to grayscale
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # Aggressive upscale (4x for low-res images, minimum 1200px width)
    h, w = gray.shape
    if w < 1200:
        scale = max(4, 1200 / w)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # Unsharp masking for sharpening blurry text
    gaussian = cv2.GaussianBlur(gray, (0, 0), 1.5)
    sharpened = cv2.addWeighted(gray, 1.8, gaussian, -0.8, 0)

    # Gentle denoise to preserve text edges
    denoised = cv2.fastNlMeansDenoising(sharpened, None, h=5, templateWindowSize=7, searchWindowSize=21)

    # Otsu's thresholding (automatic threshold selection)
    _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Convert back to PIL
    return Image.fromarray(binary)


def preprocess_image(image: Image.Image) -> Image.Image:
    """Preprocess image for better OCR accuracy.

    Uses advanced OpenCV preprocessing if available, otherwise falls back to basic PIL.
    """
    if HAS_CV2:
        return preprocess_image_advanced(image)
    return preprocess_image_basic(image)


def _count_valid_words(text: str, lang: str) -> int:
    """Count likely valid words in OCR result for quality estimation."""
    import re
    words = re.findall(r'\b[a-zA-Z가-힣]{2,}\b', text)
    # For English, check common patterns; for Korean, count Hangul words
    if lang.startswith("kor"):
        return sum(1 for w in words if any('\uac00' <= c <= '\ud7a3' for c in w))
    # English: count words with vowels (likely real words)
    return sum(1 for w in words if any(c in 'aeiouAEIOU' for c in w))


def extract_text(image: Image.Image, lang: str = "eng") -> str:
    """Extract text from a book page image using Tesseract OCR.

    Args:
        image: PIL Image of the book page
        lang: Tesseract language code ('eng', 'kor', 'eng+kor')

    Uses both basic and advanced preprocessing, returns the better result.
    """
    # PSM 6: single uniform block of text, OEM 1: LSTM only (better for books)
    config = "--psm 6 --oem 1"

    # Try basic preprocessing first
    basic_img = preprocess_image_basic(image)
    text_basic = pytesseract.image_to_string(basic_img, lang=lang, config=config).strip()

    # If OpenCV available, also try advanced and pick better result
    if HAS_CV2:
        advanced_img = preprocess_image_advanced(image)
        text_advanced = pytesseract.image_to_string(advanced_img, lang=lang, config=config).strip()

        # Pick the result with more valid words
        score_basic = _count_valid_words(text_basic, lang)
        score_advanced = _count_valid_words(text_advanced, lang)

        return text_advanced if score_advanced > score_basic else text_basic

    return text_basic


def detect_language_hint(text: str) -> str:
    """Simple heuristic to detect if text is Korean or English."""
    if not text:
        return "eng"
    korean_chars = sum(1 for c in text if '\uac00' <= c <= '\ud7a3')
    if korean_chars > len(text) * 0.3:
        return "kor"
    return "eng"
