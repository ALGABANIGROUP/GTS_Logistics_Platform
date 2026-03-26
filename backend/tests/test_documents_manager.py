from __future__ import annotations

import asyncio

from backend.bots.documents_manager import DocumentsManagerBot


def test_process_document_returns_404_for_missing_file():
    bot = DocumentsManagerBot()
    result = asyncio.run(bot.process_document("C:/missing/nonexistent-file.png"))

    assert result["success"] is False
    assert result["status_code"] == 404
    assert "Document not found" in result["error"]


def test_extract_data_uses_real_patterns():
    bot = DocumentsManagerBot()
    bot.ocr_results["DOC-1"] = {
        "text": "Invoice INV-12345 dated 2026-03-25 total $250.00 BOL-987"
    }

    result = asyncio.run(bot.extract_data("DOC-1"))
    extracted = result["extracted_data"]

    assert extracted["key_values"]["invoice_number"] == "12345"
    assert extracted["key_values"]["amount"] == "250.00"
    assert extracted["key_values"]["date"] == "2026-03-25"
    assert extracted["key_values"]["bill_of_lading_number"] == "987"
