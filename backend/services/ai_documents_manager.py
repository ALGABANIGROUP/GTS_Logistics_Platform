# backend/services/ai_documents_manager.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any

import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.document import Document

# ---------------------------------------------------------
# Safe OpenAI client accessor (Pylance-friendly)
# ---------------------------------------------------------
try:
    # We ignore type hints from the original module and wrap it
    from backend.ai.openai_safe_client import get_openai_client as _real_get_openai_client  # type: ignore[import]
except Exception:
    _real_get_openai_client = None  # type: ignore[assignment]


def get_openai_client() -> Any:
    """
    Safe wrapper that always returns Any (or None).
    This keeps Pylance happy and avoids 'Never is not awaitable' issues.
    """
    if _real_get_openai_client is None:
        return None
    try:
        return _real_get_openai_client()
    except Exception:
        return None


OPENAI_ENABLED = os.getenv("OPENAI_ENABLED", "0").lower() in ("1", "true", "yes", "on")
EXTERNAL_APIS_ENABLED = os.getenv("EXTERNAL_APIS_ENABLED", "0").lower() in (
    "1",
    "true",
    "yes",
    "on",
)


@dataclass
class DocumentInsight:
    document_id: int
    title: str
    expires_at: Optional[datetime]
    is_expiring_soon: bool
    days_remaining: Optional[int]


class AIDocumentsManager:
    """
    Lightweight document intelligence helper.

    - No OCR
    - No external heavy ML libraries
    - Optional OpenAI usage if enabled via environment
    """

    async def list_documents(self, db: AsyncSession) -> List[Document]:
        """
        Return all documents ordered by creation date (newest first).
        """
        result = await db.execute(select(Document).order_by(Document.created_at.desc()))
        docs = list(result.scalars().all())
        return docs

    def build_insight(
        self,
        doc: Document,
        warn_before_days: int = 30,
    ) -> DocumentInsight:
        """
        Compute expiration info for a single document.
        """
        expires_at = doc.expires_at
        is_expiring_soon = False
        days_remaining: Optional[int] = None

        if expires_at:
            delta = expires_at - datetime.utcnow()
            # Convert seconds to whole days (non-negative)
            days_remaining = max(int(delta.total_seconds() // 86400), 0)
            is_expiring_soon = days_remaining <= warn_before_days

        return DocumentInsight(
            document_id=doc.id,
            title=doc.title,
            expires_at=expires_at,
            is_expiring_soon=is_expiring_soon,
            days_remaining=days_remaining,
        )

    async def get_expiring_documents(
        self,
        db: AsyncSession,
        warn_before_days: int = 30,
    ) -> List[DocumentInsight]:
        """
        Return only documents that are expiring within the given window.
        """
        docs = await self.list_documents(db)
        insights: List[DocumentInsight] = []

        for doc in docs:
            insight = self.build_insight(doc, warn_before_days=warn_before_days)
            if insight.is_expiring_soon:
                insights.append(insight)

        return insights

    async def summarize_document(
        self,
        db: AsyncSession,
        document_id: int,
    ) -> Dict[str, Any]:
        """
        Build a summary for a single document.
        Uses OpenAI only if enabled; otherwise returns a metadata-based summary.
        """
        result = await db.execute(select(Document).where(Document.id == document_id))
        doc = result.scalar_one_or_none()

        if not doc:
            return {
                "document_id": document_id,
                "summary": "Document not found.",
            }

        base_summary_parts: List[str] = [
            f"Document '{doc.title}' owned by user {doc.owner_id}."
        ]

        if doc.file_type:
            base_summary_parts.append(f"File type: {doc.file_type}.")
        if doc.expires_at:
            base_summary_parts.append(f"Expires at {doc.expires_at.isoformat()}.")

        base_summary = " ".join(base_summary_parts)

        ai_summary: Optional[str] = None

        # Optional AI analysis
        if OPENAI_ENABLED and EXTERNAL_APIS_ENABLED:
            client = get_openai_client()
            if client is not None:
                try:
                    summary_text = base_summary
                    prompt = (
                        "You are an assistant summarizing logistics documents.\n\n"
                        f"Metadata:\n"
                        f"- Title: {doc.title}\n"
                        f"- Type: {doc.file_type or 'unknown'}\n"
                        f"- Expires: {doc.expires_at or 'none'}\n\n"
                        "Provide a short, high-level summary (maximum 3 bullet points) "
                        "of how this type of document is typically used in a trucking / logistics company."
                    )

                    resp = await client.chat.completions.create(  # type: ignore[call-arg]
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a concise logistics documentation assistant.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.3,
                        max_tokens=300,
                    )
                    if resp and resp.choices:
                        content = resp.choices[0].message.content or ""
                        ai_summary = content.strip() or None
                except Exception:
                    ai_summary = None

        return {
            "document_id": doc.id,
            "title": doc.title,
            "base_summary": base_summary,
            "ai_summary": ai_summary or base_summary,
        }


# Global singleton for reuse
_documents_manager = AIDocumentsManager()


def get_ai_documents_manager() -> AIDocumentsManager:
    """
    Accessor used by routes or other services.

    Example usage in a route:

        from fastapi import Depends
        from sqlalchemy.ext.asyncio import AsyncSession
        from backend.database.config import get_db
        from backend.services.ai_documents_manager import get_ai_documents_manager

        @router.get("/documents/expiring")
        async def expiring(db: AsyncSession = Depends(get_db)):
            mgr = get_ai_documents_manager()
            return await mgr.get_expiring_documents(db, warn_before_days=30)
    """
    return _documents_manager

