# pyright: reportArgumentType=false, reportAttributeAccessIssue=false
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.partner import Partner, PartnerAgreement
from backend.schemas.partner import (
    PartnerAgreementCurrentResponse,
    PartnerAgreementSignRequest,
    PartnerAgreementSignResponse,
)

AGREEMENT_VERSION = "1.0"
AGREEMENT_FILE_PATH = (
    Path(__file__).resolve().parent.parent / "legal" / "partner_agreement_v1.md"
)


def _load_agreement_text() -> str:
    if not AGREEMENT_FILE_PATH.exists():
        raise FileNotFoundError(f"Agreement file not found at {AGREEMENT_FILE_PATH}")
    return AGREEMENT_FILE_PATH.read_text(encoding="utf-8")


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


async def get_current_agreement() -> PartnerAgreementCurrentResponse:
    body = _load_agreement_text()
    text_hash = _hash_text(body)
    return PartnerAgreementCurrentResponse(
        agreement_version=AGREEMENT_VERSION,
        agreement_body=body,
        agreement_text_hash=text_hash,
    )


async def sign_agreement(
    db: AsyncSession,
    *,
    partner_id: UUID,
    request: PartnerAgreementSignRequest,
    ip_address: Optional[str],
    user_agent: Optional[str],
) -> PartnerAgreementSignResponse:
    if not (
        request.checkbox_revenue
        and request.checkbox_confidentiality
        and request.checkbox_misuse
    ):
        raise ValueError("All agreement checkboxes must be accepted.")

    partner: Partner | None = await db.scalar(
        select(Partner).where(Partner.id == partner_id)
    )
    if partner is None:
        raise ValueError("Partner not found")

    body = _load_agreement_text()
    text_hash = _hash_text(body)

    signed_at = datetime.now(timezone.utc)
    signature_payload = (
        f"{partner_id}|{request.signature_name}|{signed_at.isoformat()}|{ip_address or ''}"
    )
    signature_hash = _hash_text(signature_payload)

    # deactivate previous agreements for this partner
    await db.execute(
        update(PartnerAgreement)
        .where(
            PartnerAgreement.partner_id == partner_id,
            PartnerAgreement.is_active.is_(True),
        )
        .values(is_active=False)
    )

    # build kwargs dict to avoid strict type checking per field
    data: Dict[str, Any] = {
        "partner_id": partner_id,
        "agreement_version": request.agreement_version,
        "agreement_text_hash": text_hash,
        "signed_at": signed_at,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "signature_name": request.signature_name,
        "signature_hash": signature_hash,
        "pdf_url": None,
        "is_active": True,
    }

    agreement = PartnerAgreement(**data)  # type: ignore[arg-type]
    db.add(agreement)

    # update partner status after signature
    partner.status = "active"  # type: ignore[assignment]

    await db.flush()
    await db.refresh(agreement)

    return PartnerAgreementSignResponse(
        partner_id=partner_id,
        agreement_version=agreement.agreement_version,
        signed_at=agreement.signed_at,
        ip_address=agreement.ip_address,
        signature_name=agreement.signature_name,
    )

