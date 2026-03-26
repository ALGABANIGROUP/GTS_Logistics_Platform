# backend/bots/documents_manager.py
"""
Documents Manager Bot
Handles document OCR, classification, and management.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

from backend.services.documents_manager import DocumentsManagerService, OCRServiceUnavailable


class DocumentsManagerBot:
    """Documents Manager - OCR and document processing"""

    def __init__(self):
        self.name = "documents_manager"
        self.display_name = "📄 Documents Manager"
        self.description = "Document OCR and classification"
        self.version = "1.0.0"
        self.mode = "infrastructure"
        self.is_active = True

        # Document data structures
        self.documents: List[Dict] = []
        self.ocr_results: Dict[str, Dict] = {}
        self.classification_rules: Dict[str, str] = {}
        self.service = DocumentsManagerService()

    async def run(self, payload: dict) -> dict:
        """Main execution method"""
        action = payload.get("action", "status")

        if action == "status":
            return await self.status()
        elif action == "process_document":
            return await self.process_document(payload.get("document_path", ""))
        elif action == "classify_document":
            return await self.classify_document(payload.get("content", ""))
        elif action == "get_documents":
            return await self.get_documents()
        elif action == "search_documents":
            return await self.search_documents(payload.get("query", ""))
        elif action == "extract_data":
            return await self.extract_data(payload.get("document_id", ""))
        else:
            return {"error": f"Unknown action: {action}"}

    async def status(self) -> dict:
        """Return bot health/status."""
        return {
            "ok": True,
            "bot": self.name,
            "version": self.version,
            "total_documents": len(self.documents),
            "processed_today": len([d for d in self.documents if d.get("processed_at", "").startswith(datetime.now().date().isoformat())]),
            "message": "Document processing operational"
        }

    async def process_document(self, document_path: str) -> dict:
        """Process a document with OCR"""
        document_id = f"DOC-{len(self.documents) + 1}"
        document = {
            "id": document_id,
            "path": document_path,
            "status": "processing",
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "processed_at": None
        }
        self.documents.append(document)
        try:
            ocr_result = self.service.process_document(document_path)
        except OCRServiceUnavailable as exc:
            document["status"] = "failed"
            document["processed_at"] = datetime.now(timezone.utc).isoformat()
            return {
                "success": False,
                "status_code": 503,
                "error": str(exc),
                "document": document,
            }

        if not ocr_result.get("success"):
            document["status"] = "failed"
            document["processed_at"] = datetime.now(timezone.utc).isoformat()
            return {
                "success": False,
                "status_code": ocr_result.get("status_code", 500),
                "error": ocr_result.get("error", "Document processing failed"),
                "document": document,
            }

        self.ocr_results[document_id] = ocr_result

        document["status"] = "completed"
        document["processed_at"] = datetime.now(timezone.utc).isoformat()

        return {"success": True, "document": document, "ocr_result": ocr_result}

    async def classify_document(self, content: str) -> dict:
        """Classify document type based on content"""
        return self.service.classify_document(content)

    async def get_documents(self) -> dict:
        """Get all documents"""
        return {"documents": self.documents}

    async def search_documents(self, query: str) -> dict:
        """Search documents by content"""
        results = []
        for doc in self.documents:
            doc_id = doc["id"]
            if doc_id in self.ocr_results:
                text = self.ocr_results[doc_id].get("text", "")
                if query.lower() in text.lower():
                    results.append(doc)
        return {"results": results}

    async def extract_data(self, document_id: str) -> dict:
        """Extract structured data from document"""
        if document_id not in self.ocr_results:
            return {"error": "Document not found or not processed"}

        text = self.ocr_results[document_id].get("text", "")

        extracted_data = self.service.extract_data(text)

        return {"document_id": document_id, "extracted_data": extracted_data}
