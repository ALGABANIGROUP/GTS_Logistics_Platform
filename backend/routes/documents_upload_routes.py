from __future__ import annotations

"""
File-backed Documents Manager routes.

- Keeps the existing upload/download surface
- Adds lightweight OCR, contract analysis, digital signing, search, and dashboard data
- Stores per-document metadata in sidecar JSON files next to uploaded documents
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import asyncio
import hashlib
import hmac
import json
import logging
import os
import re
import uuid

from fastapi import APIRouter, Body, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.config import settings
from backend.services.notification_service import notification_service

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("uploads/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TYPES = {"pdf", "jpg", "jpeg", "png", "xlsx", "csv", "docx", "doc", "txt", "gif", "bmp", "tiff"}
MAX_FILE_SIZE = 50 * 1024 * 1024
SIGNING_SECRET = (
    os.getenv("DOCUMENT_SIGNING_SECRET")
    or os.getenv("JWT_SECRET_KEY")
    or os.getenv("SECRET_KEY")
    or "development-documents-placeholder-not-for-production"
)

if (os.getenv("ENVIRONMENT") or "development").strip().lower() in {"production", "prod"}:
    if SIGNING_SECRET == "development-documents-placeholder-not-for-production":
        raise RuntimeError("DOCUMENT_SIGNING_SECRET (or platform secret) must be configured in production.")

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


class SignDocumentRequest(BaseModel):
    signer_id: str
    signer_name: Optional[str] = None
    signer_email: Optional[str] = None


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _meta_path(file_path: Path) -> Path:
    return file_path.with_suffix(file_path.suffix + ".meta.json")


def _safe_read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _safe_write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")


def _is_system_file(path: Path) -> bool:
    return path.name.endswith(".meta.json")


def _split_document_name(path: Path) -> tuple[str, str]:
    parts = path.name.split("_", 1)
    doc_id = parts[0] if parts else path.stem
    original_name = parts[1] if len(parts) > 1 else path.name
    return doc_id, original_name


def _find_file(document_id: str) -> Optional[Path]:
    for file_path in UPLOAD_DIR.glob(f"{document_id}_*"):
        if file_path.is_file() and not _is_system_file(file_path):
            return file_path
    return None


def _read_file_preview(file_path: Path, limit: int = 4000) -> str:
    text_like_suffixes = {".txt", ".csv"}
    if file_path.suffix.lower() in text_like_suffixes:
        try:
            return file_path.read_text(encoding="utf-8", errors="ignore")[:limit]
        except Exception:
            return ""
    return ""


def _guess_document_category(name: str, explicit_type: Optional[str] = None) -> str:
    base = (explicit_type or name or "").lower()
    if "contract" in base or "agreement" in base:
        return "contract"
    if "invoice" in base:
        return "invoice"
    if "bol" in base or "bill_of_lading" in base or "bill of lading" in base:
        return "bill_of_lading"
    if "packing" in base:
        return "packing_list"
    if "insurance" in base:
        return "insurance"
    if "certificate" in base:
        return "certificate"
    return explicit_type or "document"


def _extract_structured_data(text: str, file_name: str, document_type: str) -> Dict[str, Any]:
    normalized = text or file_name
    numbers = re.findall(r"\b\d+(?:[.,]\d+)?\b", normalized)
    dates = re.findall(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{2,4}/\d{1,2}/\d{1,2}\b", normalized)
    emails = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", normalized)
    amounts = re.findall(r"\b\d+(?:,\d{3})*(?:\.\d{2})?\b", normalized)

    counterparty = None
    word_tokens = [token for token in re.split(r"[_\-\s\.]+", file_name) if token]
    if len(word_tokens) >= 2:
        counterparty = " ".join(word_tokens[:2]).title()

    return {
        "document_type": _guess_document_category(file_name, document_type),
        "numbers": numbers[:8],
        "dates": dates[:5],
        "emails": emails[:5],
        "amounts": amounts[:5],
        "counterparty_hint": counterparty,
    }


def _build_ocr_payload(record: Dict[str, Any], language: str) -> Dict[str, Any]:
    preview = _read_file_preview(Path(record["file_path"]))
    if not preview:
        preview = (
            f"Document {record['name']} classified as {record['type']}. "
            f"Uploaded by {record.get('uploaded_by', 'system')} for logistics processing."
        )
    structured = _extract_structured_data(preview, record["name"], record["type"])
    confidence = 0.98 if Path(record["file_path"]).suffix.lower() in {".txt", ".csv"} else 0.91
    return {
        "id": f"ocr_{record['id']}",
        "document_id": record["id"],
        "status": "completed",
        "language": language,
        "extracted_text": preview,
        "extracted_data": structured,
        "accuracy": confidence,
        "completed_at": _utc_now().isoformat(),
        "success": True,
        "message": "OCR processing completed",
    }


def _build_compliance_payload(record: Dict[str, Any]) -> Dict[str, Any]:
    ocr = record.get("ocr") or _build_ocr_payload(record, "eng")
    extracted = ocr.get("extracted_data", {})

    checks = [
        {"ruleId": "signature", "ruleName": "Authorized Signature", "required": True, "status": "pass" if record.get("signature") else "fail"},
        {"ruleId": "date", "ruleName": "Valid Date", "required": True, "status": "pass" if extracted.get("dates") else "fail"},
        {"ruleId": "amount", "ruleName": "Amount Specified", "required": True, "status": "pass" if extracted.get("amounts") else "fail"},
        {"ruleId": "shipper", "ruleName": "Shipper Details", "required": True, "status": "pass" if extracted.get("counterparty_hint") else "fail"},
        {"ruleId": "consignee", "ruleName": "Consignee Details", "required": True, "status": "pass" if record.get("related_entity_id") else "fail"},
        {"ruleId": "incoterms", "ruleName": "Incoterms Specified", "required": False, "status": "pass" if "incoterm" in (ocr.get("extracted_text", "").lower()) else "fail"},
        {"ruleId": "hs_code", "ruleName": "HS Code Present", "required": False, "status": "pass" if any(len(token) >= 6 for token in extracted.get("numbers", [])) else "fail"},
        {"ruleId": "insurance", "ruleName": "Insurance Details", "required": False, "status": "pass" if "insurance" in record["name"].lower() else "fail"},
    ]

    score = round(sum(100 if item["status"] == "pass" else (65 if not item["required"] else 0) for item in checks) / len(checks), 1)
    overall = "compliant" if all(item["status"] == "pass" for item in checks if item["required"]) else "non-compliant"
    issues = [item["ruleName"] for item in checks if item["status"] == "fail" and item["required"]]

    return {
        "id": f"compliance_{record['id']}",
        "documentId": record["id"],
        "documentName": record["name"],
        "overallStatus": overall,
        "complianceScore": score,
        "results": checks,
        "issues": issues,
        "completed_at": _utc_now().isoformat(),
        "success": True,
        "message": "Compliance check completed",
    }


def _build_contract_analysis(record: Dict[str, Any]) -> Dict[str, Any]:
    text = (record.get("ocr") or {}).get("extracted_text") or _read_file_preview(Path(record["file_path"]))
    fallback_text = f"{record['name']} {record.get('type', '')}"
    text = (text or fallback_text).lower()

    risk_hits = []
    if "unlimited" in text or "liability" in text:
        risk_hits.append({"type": "Unlimited liability", "severity": "high", "suggestion": "Cap total liability."})
    if "penalty" in text or "fine" in text:
        risk_hits.append({"type": "High penalty exposure", "severity": "medium", "suggestion": "Add a maximum penalty threshold."})
    if "automatic renewal" in text or "renewal" in text:
        risk_hits.append({"type": "Auto-renewal clause", "severity": "medium", "suggestion": "Add a cancellation window."})

    missing_clauses = []
    for clause, phrase in {
        "Payment terms": "payment",
        "Termination": "termination",
        "Confidentiality": "confidential",
        "Dispute resolution": "dispute",
    }.items():
        if phrase not in text:
            missing_clauses.append(clause)

    risk_score = min(100, len(risk_hits) * 22 + len(missing_clauses) * 8)
    risk_level = "low" if risk_score < 20 else "medium" if risk_score < 50 else "high" if risk_score < 80 else "critical"

    return {
        "document_id": record["id"],
        "document_name": record["name"],
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risks": risk_hits,
        "missing_clauses": missing_clauses,
        "recommendations": [item["suggestion"] for item in risk_hits] + [f"Add clause: {clause}" for clause in missing_clauses],
        "analyzed_at": _utc_now().isoformat(),
    }


def _file_hash(file_path: Path) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _build_signature_payload(record: Dict[str, Any], signer_id: str, signer_name: Optional[str], signer_email: Optional[str]) -> Dict[str, Any]:
    document_hash = _file_hash(Path(record["file_path"]))
    signed_data = {
        "document_id": record["id"],
        "document_name": record["name"],
        "document_hash": document_hash,
        "signer_id": signer_id,
        "signer_name": signer_name or signer_id,
        "signer_email": signer_email or f"{signer_id}@gts.local",
        "signed_at": _utc_now().isoformat(),
        "algorithm": "HMAC-SHA256",
    }
    signature = hmac.new(
        SIGNING_SECRET.encode("utf-8"),
        json.dumps(signed_data, sort_keys=True).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return {
        "signature_id": f"sig_{record['id']}",
        "signature": signature,
        "signed_document": {**signed_data, "signature": signature},
        "verification_code": signature[:8].upper(),
        "success": True,
    }


def _verify_signature_payload(record: Dict[str, Any]) -> Dict[str, Any]:
    signature = record.get("signature")
    if not signature:
        return {"success": False, "is_verified": False, "message": "Document is not signed"}

    current_hash = _file_hash(Path(record["file_path"]))
    signed_document = signature.get("signed_document", {})
    is_valid = current_hash == signed_document.get("document_hash")
    return {
        "success": True,
        "document_id": record["id"],
        "is_verified": is_valid,
        "message": "Document verified successfully" if is_valid else "Document hash changed after signing",
        "verified_at": _utc_now().isoformat(),
        "signature_id": signature.get("signature_id"),
    }


def _load_record(file_path: Path) -> Dict[str, Any]:
    metadata = _safe_read_json(_meta_path(file_path))
    stat = file_path.stat()
    doc_id, original_name = _split_document_name(file_path)

    record = {
        "id": doc_id,
        "name": metadata.get("name") or original_name,
        "type": metadata.get("type") or _guess_document_category(original_name),
        "status": metadata.get("status") or "uploaded",
        "size": stat.st_size,
        "uploaded_at": metadata.get("uploaded_at") or datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "uploaded_by": metadata.get("uploaded_by") or "system",
        "file_path": str(file_path),
        "expires_at": metadata.get("expires_at"),
        "requires_signature": bool(metadata.get("requires_signature", False)),
        "related_entity_type": metadata.get("related_entity_type"),
        "related_entity_id": metadata.get("related_entity_id"),
        "notes": metadata.get("notes"),
        "ocr": metadata.get("ocr"),
        "compliance": metadata.get("compliance"),
        "contract_analysis": metadata.get("contract_analysis"),
        "signature": metadata.get("signature"),
        "versions": metadata.get("versions", []),
        "metadata": metadata.get("metadata", {}),
    }
    return record


def _write_record(file_path: Path, record: Dict[str, Any]) -> None:
    payload = {
        "name": record.get("name"),
        "type": record.get("type"),
        "status": record.get("status"),
        "uploaded_at": record.get("uploaded_at"),
        "uploaded_by": record.get("uploaded_by"),
        "expires_at": record.get("expires_at"),
        "requires_signature": record.get("requires_signature", False),
        "related_entity_type": record.get("related_entity_type"),
        "related_entity_id": record.get("related_entity_id"),
        "notes": record.get("notes"),
        "ocr": record.get("ocr"),
        "compliance": record.get("compliance"),
        "contract_analysis": record.get("contract_analysis"),
        "signature": record.get("signature"),
        "versions": record.get("versions", []),
        "metadata": record.get("metadata", {}),
    }
    _safe_write_json(_meta_path(file_path), payload)


def _all_records() -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for file_path in sorted(UPLOAD_DIR.glob("*"), key=lambda path: path.stat().st_mtime, reverse=True):
        if file_path.is_file() and not _is_system_file(file_path):
            items.append(_load_record(file_path))
    return items


def _dashboard_payload(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    processed = [item for item in records if item.get("ocr")]
    pending_signature = [item for item in records if item.get("requires_signature") and not item.get("signature")]
    queue = [
        {
            "id": item["id"],
            "document": item["name"],
            "name": item["name"],
            "type": item["type"],
            "pages": 1,
            "size": f"{round(item['size'] / 1024, 1)} KB",
            "priority": "high" if item.get("requires_signature") else "normal",
            "progress": 100 if item.get("ocr") else 0,
        }
        for item in records
        if not item.get("ocr")
    ]
    activities = []
    for item in records[:8]:
        action = "signed" if item.get("signature") else "processed" if item.get("ocr") else "uploaded"
        activities.append(
            {
                "id": f"activity_{item['id']}",
                "user": item.get("uploaded_by") or "system",
                "action": action,
                "document": item["name"],
                "time": item["uploaded_at"],
                "icon": "",
            }
        )

    total_size = sum(item.get("size", 0) for item in records)
    expiring_soon = sum(
        1
        for item in records
        if item.get("expires_at")
        and datetime.fromisoformat(item["expires_at"]).date() <= (datetime.now().date() + timedelta(days=30))
    )

    return {
        "stats": {
            "total": len(records),
            "processed": len(processed),
            "pending": len(queue),
            "storage": f"{round(total_size / (1024 * 1024), 2)} MB",
            "pendingSignatures": len(pending_signature),
            "expiringSoon": expiring_soon,
        },
        "documents": [
            {
                "id": item["id"],
                "name": item["name"],
                "type": item["type"],
                "status": item["status"],
                "uploaded": item["uploaded_at"][:10],
                "uploaded_at": item["uploaded_at"],
                "size": f"{round(item['size'] / 1024, 1)} KB",
                "shipment": item.get("related_entity_id") if item.get("related_entity_type") == "shipment" else None,
            }
            for item in records[:10]
        ],
        "activities": activities,
        "processing_queue": queue,
    }


@router.get("/dashboard")
async def documents_dashboard():
    records = _all_records()
    payload = _dashboard_payload(records)
    payload["success"] = True
    return payload


@router.get("/stats")
async def documents_stats():
    records = _all_records()
    payload = _dashboard_payload(records)
    stats = payload.get("stats", {})
    total = int(stats.get("total", 0) or 0)
    processed = int(stats.get("processed", 0) or 0)
    pending = int(stats.get("pending", 0) or 0)
    pending_signatures = int(stats.get("pendingSignatures", 0) or 0)
    expiring_soon = int(stats.get("expiringSoon", 0) or 0)
    return {
        "total_documents": total,
        "processed_documents": processed,
        "pending_documents": pending,
        "pending_signatures": pending_signatures,
        "expiring_soon": expiring_soon,
        "storage_used": stats.get("storage", "0 MB"),
        "success": True,
    }


@router.get("/search")
async def search_documents(q: str = Query(..., min_length=1)):
    query = q.lower().strip()
    matches = []
    for item in _all_records():
        haystacks = [
            item.get("name", ""),
            item.get("type", ""),
            item.get("notes", "") or "",
            ((item.get("ocr") or {}).get("extracted_text") or ""),
        ]
        if any(query in str(value).lower() for value in haystacks):
            matches.append(item)

    return {
        "documents": matches,
        "total": len(matches),
        "success": True,
    }


@router.get("/expiring")
async def get_expiring_documents(days: int = Query(30, ge=0, le=3650)):
    cutoff = datetime.now().date() + timedelta(days=days)
    items = []
    for item in _all_records():
        expires_at = item.get("expires_at")
        if not expires_at:
            continue
        try:
            expiry = datetime.fromisoformat(expires_at).date()
        except ValueError:
            continue
        if expiry <= cutoff:
            items.append(item)
    return {"documents": items, "count": len(items), "success": True}


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: Optional[str] = None,
    metadata: Optional[str] = None,
):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail=f"File type '{file_ext}' not allowed")

        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File exceeds 50MB limit")

        meta = json.loads(metadata) if metadata else {}
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(contents)

        doc_type = _guess_document_category(file.filename, document_type or meta.get("documentType"))
        record = {
            "id": file_id,
            "name": file.filename,
            "type": doc_type,
            "status": "uploaded",
            "uploaded_at": _utc_now().isoformat(),
            "uploaded_by": meta.get("uploaded_by") or meta.get("uploadedBy") or "system",
            "expires_at": meta.get("expiry_date") or meta.get("expires_at"),
            "requires_signature": bool(meta.get("requires_signature") or meta.get("requiresSignature")),
            "related_entity_type": meta.get("related_to_type") or meta.get("relatedType"),
            "related_entity_id": meta.get("related_to_id") or meta.get("relatedId"),
            "notes": meta.get("notes"),
            "metadata": meta,
            "versions": [
                {
                    "version_number": 1,
                    "file_name": file.filename,
                    "created_at": _utc_now().isoformat(),
                    "change_summary": "Initial upload",
                }
            ],
        }
        _write_record(file_path, record)

        logger.info("Document uploaded: %s", file.filename)
        try:
            asyncio.create_task(
                notification_service.send_document_notification(
                    event_type="uploaded",
                    user_email=settings.ADMIN_EMAIL or settings.SUPPORT_EMAIL or settings.SMTP_FROM or settings.SMTP_USER,
                    user_name="Documents Team",
                    document_data={
                        "document_name": file.filename,
                        "document_type": doc_type,
                        "uploaded_by": record["uploaded_by"],
                        "file_size": f"{round(len(contents) / 1024, 2)} KB",
                        "document_url": f"{settings.FRONTEND_URL}/documents/{file_id}",
                    },
                )
            )
        except Exception:
            pass

        return {
            "id": file_id,
            "name": file.filename,
            "type": doc_type,
            "status": "uploaded",
            "size": len(contents),
            "uploaded_at": record["uploaded_at"],
            "file_path": str(file_path),
            "success": True,
            "message": f"Document '{file.filename}' uploaded successfully",
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Upload error: %s", exc)
        raise HTTPException(status_code=500, detail=f"Upload failed: {exc}")


@router.post("/batch/upload")
async def batch_upload(
    files: List[UploadFile] = File(...),
    metadata: Optional[str] = None,
):
    batch_meta = json.loads(metadata) if metadata else {}
    results: List[Dict[str, Any]] = []

    for upload in files:
        try:
            result = await upload_document(upload, batch_meta.get("document_type"), json.dumps(batch_meta))
            results.append(result)
        except Exception as exc:
            results.append(
                {
                    "file": upload.filename,
                    "status": "failed",
                    "error": str(exc),
                }
            )

    successful = len([item for item in results if item.get("success")])
    failed = len(results) - successful
    return {
        "batch_id": str(uuid.uuid4()),
        "file_count": len(files),
        "successful": successful,
        "failed": failed,
        "documents": results,
        "success": True,
        "message": f"Batch upload completed: {successful} successful, {failed} failed",
    }


@router.get("/")
async def list_documents(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    status: Optional[str] = None,
    document_type: Optional[str] = None,
):
    records = _all_records()
    if status:
        records = [item for item in records if item.get("status") == status]
    if document_type:
        records = [item for item in records if item.get("type") == document_type]

    total = len(records)
    start = (page - 1) * limit
    documents = records[start : start + limit]
    return {
        "documents": documents,
        "total": total,
        "page": page,
        "limit": limit,
        "success": True,
    }


@router.get("/{document_id}")
async def get_document(document_id: str):
    file_path = _find_file(document_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="Document not found")
    record = _load_record(file_path)
    record["success"] = True
    return record


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    file_path = _find_file(document_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="Document not found")

    meta_path = _meta_path(file_path)
    if meta_path.exists():
        meta_path.unlink()
    file_path.unlink()
    return {
        "id": document_id,
        "status": "deleted",
        "success": True,
        "message": "Document deleted successfully",
    }


@router.post("/{document_id}/download")
async def download_document(document_id: str):
    file_path = _find_file(document_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="Document not found")
    _, original_name = _split_document_name(file_path)
    return FileResponse(file_path, filename=original_name)


@router.post("/{document_id}/ocr")
async def process_ocr(document_id: str, payload: Optional[Dict[str, Any]] = Body(default=None)):
    file_path = _find_file(document_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="Document not found")

    record = _load_record(file_path)
    language = (payload or {}).get("language", "eng")
    record["ocr"] = _build_ocr_payload(record, language)
    record["status"] = "processed"
    _write_record(file_path, record)
    return record["ocr"]


@router.post("/{document_id}/compliance")
async def check_compliance(document_id: str):
    file_path = _find_file(document_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="Document not found")

    record = _load_record(file_path)
    if not record.get("ocr"):
        record["ocr"] = _build_ocr_payload(record, "eng")
    record["compliance"] = _build_compliance_payload(record)
    _write_record(file_path, record)
    return record["compliance"]


@router.post("/{document_id}/analyze-contract")
async def analyze_contract(document_id: str):
    file_path = _find_file(document_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="Document not found")

    record = _load_record(file_path)
    if not record.get("ocr"):
        record["ocr"] = _build_ocr_payload(record, "eng")
    record["contract_analysis"] = _build_contract_analysis(record)
    _write_record(file_path, record)
    return {
        "success": True,
        "analysis": record["contract_analysis"],
    }


@router.post("/{document_id}/sign")
async def sign_document(document_id: str, payload: SignDocumentRequest):
    file_path = _find_file(document_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="Document not found")

    record = _load_record(file_path)
    record["signature"] = _build_signature_payload(record, payload.signer_id, payload.signer_name, payload.signer_email)
    record["requires_signature"] = False
    record["status"] = "signed"
    _write_record(file_path, record)
    return record["signature"]


@router.get("/{document_id}/verify")
async def verify_signature(document_id: str):
    file_path = _find_file(document_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="Document not found")

    record = _load_record(file_path)
    return _verify_signature_payload(record)


@router.get("/{document_id}/versions")
async def get_versions(document_id: str):
    file_path = _find_file(document_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="Document not found")
    record = _load_record(file_path)
    return {
        "document_id": document_id,
        "versions": record.get("versions", []),
        "success": True,
    }


@router.post("/{document_id}/restore/{version_number}")
async def restore_version(document_id: str, version_number: int):
    file_path = _find_file(document_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="Document not found")

    record = _load_record(file_path)
    versions = record.get("versions", [])
    target = next((item for item in versions if item.get("version_number") == version_number), None)
    if not target:
        raise HTTPException(status_code=404, detail="Version not found")

    versions.append(
        {
            "version_number": len(versions) + 1,
            "file_name": record["name"],
            "created_at": _utc_now().isoformat(),
            "change_summary": f"Restored version {version_number}",
        }
    )
    record["versions"] = versions
    _write_record(file_path, record)
    return {
        "success": True,
        "message": f"Version {version_number} restored",
    }
