from __future__ import annotations

import io
import logging
from pathlib import Path
import re
from typing import Any, Dict

logger = logging.getLogger(__name__)


class OCRServiceUnavailable(RuntimeError):
    """Raised when OCR processing cannot be executed with the current environment."""


class DocumentsManagerService:
    """Real document processing service backed by installed OCR libraries."""

    def __init__(self) -> None:
        self._ocr_ready = False
        self._pdf_ready = False
        self._init_ocr_backends()

    def _init_ocr_backends(self) -> None:
        try:
            from PIL import Image  # noqa: F401
            import pytesseract  # noqa: F401

            self._ocr_ready = True
        except Exception as exc:
            logger.warning("OCR backend not available: %s", exc)
            self._ocr_ready = False

        try:
            from pdf2image import convert_from_bytes  # noqa: F401

            self._pdf_ready = True
        except Exception:
            self._pdf_ready = False

    def process_document(self, document_path: str) -> Dict[str, Any]:
        path = Path(document_path)
        if not path.exists() or not path.is_file():
            return {
                "success": False,
                "status_code": 404,
                "error": f"Document not found: {document_path}",
            }

        if not self._ocr_ready:
            raise OCRServiceUnavailable(
                "OCR service requires valid runtime dependencies. Install Pillow and pytesseract."
            )

        suffix = path.suffix.lower()
        if suffix not in {".png", ".jpg", ".jpeg", ".pdf"}:
            return {
                "success": False,
                "status_code": 400,
                "error": f"Unsupported document type: {suffix or 'unknown'}",
            }

        if suffix == ".pdf" and not self._pdf_ready:
            raise OCRServiceUnavailable(
                "PDF OCR requires pdf2image to be installed and configured."
            )

        text = self._extract_text(path, suffix)
        if not text.strip():
            return {
                "success": False,
                "status_code": 422,
                "error": "OCR extracted no text from the document",
            }

        return {
            "success": True,
            "status_code": 200,
            "text": text,
            "confidence": None,
            "language": "en",
        }

    def _extract_text(self, path: Path, suffix: str) -> str:
        from PIL import Image
        import pytesseract

        content = path.read_bytes()
        if suffix == ".pdf":
            from pdf2image import convert_from_bytes

            images = convert_from_bytes(content)
            return "\n".join(pytesseract.image_to_string(image) for image in images)

        image = Image.open(io.BytesIO(content))
        return pytesseract.image_to_string(image)

    def classify_document(self, content: str) -> Dict[str, Any]:
        content_lower = content.lower()
        if "invoice" in content_lower:
            return {"document_type": "invoice", "confidence": 0.9}
        if "bill of lading" in content_lower or "bol" in content_lower:
            return {"document_type": "bill_of_lading", "confidence": 0.88}
        if "customs" in content_lower:
            return {"document_type": "customs_form", "confidence": 0.85}
        if "contract" in content_lower:
            return {"document_type": "contract", "confidence": 0.82}
        if "report" in content_lower:
            return {"document_type": "report", "confidence": 0.8}
        return {"document_type": "general", "confidence": 0.5}

    def extract_data(self, text: str) -> Dict[str, Any]:
        invoice_number = (
            self._extract_pattern(text, r"\bINV\b[-:\s]*([A-Z0-9-]+)\b")
            or self._extract_pattern(text, r"\bINVOICE(?:\s+NUMBER|\s+NO\.?)?[-:\s]*([A-Z0-9-]+)\b")
        )
        amount = self._extract_pattern(text, r"\$\s?([0-9,]+(?:\.[0-9]{2})?)")
        date = self._extract_pattern(text, r"\b(20\d{2}-\d{2}-\d{2})\b")
        bol_number = self._extract_pattern(text, r"\bBOL[-:\s]*([A-Z0-9-]+)\b")

        entities = []
        if invoice_number:
            entities.append({"type": "invoice_number", "value": invoice_number})
        if amount:
            entities.append({"type": "amount", "value": amount})
        if date:
            entities.append({"type": "date", "value": date})
        if bol_number:
            entities.append({"type": "bill_of_lading_number", "value": bol_number})

        return {
            "entities": entities,
            "key_values": {
                "invoice_number": invoice_number,
                "amount": amount,
                "date": date,
                "bill_of_lading_number": bol_number,
            },
            "summary": f"Document contains {len(text)} characters",
        }

    def _extract_pattern(self, text: str, pattern: str) -> str | None:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            return None
        if match.lastindex:
            return match.group(1)
        return match.group(0)
