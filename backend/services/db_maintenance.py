from __future__ import annotations

from typing import Dict, List

from sqlalchemy import text

from backend.database.config import get_sessionmaker


INDEX_STATEMENTS = [
    "CREATE INDEX IF NOT EXISTS ix_shipments_status ON shipments(status)",
    "CREATE INDEX IF NOT EXISTS ix_invoices_status ON invoices(status)",
    "CREATE INDEX IF NOT EXISTS ix_email_messages_created_at ON email_messages(created_at)",
]


async def ensure_maintenance_indexes() -> Dict[str, List[str]]:
    maker = get_sessionmaker()
    executed: List[str] = []
    skipped: List[str] = []
    async with maker() as session:
        for statement in INDEX_STATEMENTS:
            try:
                await session.execute(text(statement))
                executed.append(statement)
            except Exception:
                skipped.append(statement)
        try:
            await session.execute(text("ANALYZE"))
            executed.append("ANALYZE")
        except Exception:
            skipped.append("ANALYZE")
        await session.commit()
    return {"executed": executed, "skipped": skipped}

