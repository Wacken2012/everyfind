#!/usr/bin/env python3
"""Example OCR plugin (optional dependency on pytesseract)."""
from __future__ import annotations

from typing import Dict, Any
try:
    import pytesseract
    from PIL import Image
except Exception:
    pytesseract = None


class Plugin:
    def metadata(self) -> Dict[str, Any]:
        return {
            'name': 'ocr',
            'description': 'Extract text from images using Tesseract (optional)'
        }

    def run(self, image_path: str) -> str:
        if pytesseract is None:
            raise RuntimeError('pytesseract not installed')
        img = Image.open(image_path)
        return pytesseract.image_to_string(img)
