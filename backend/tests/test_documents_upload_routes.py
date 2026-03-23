from pathlib import Path

from backend.routes.documents_upload_routes import (
    _build_compliance_payload,
    _build_contract_analysis,
    _build_signature_payload,
    _verify_signature_payload,
)


def _record(tmp_path: Path, name: str = "partner_contract.txt") -> dict:
    file_path = tmp_path / name
    file_path.write_text(
        "Contract payment terms renewal liability penalty dispute confidential",
        encoding="utf-8",
    )
    return {
        "id": "doc-1",
        "name": name,
        "type": "contract",
        "file_path": str(file_path),
        "uploaded_by": "tester",
        "related_entity_id": "shipment-1",
        "requires_signature": True,
        "ocr": {
            "extracted_text": file_path.read_text(encoding="utf-8"),
            "extracted_data": {
                "dates": ["2026-03-19"],
                "amounts": ["5000.00"],
                "counterparty_hint": "Partner Logistics",
            },
        },
    }


def test_contract_analysis_detects_risk_and_missing_clauses(tmp_path: Path):
    record = _record(tmp_path)
    analysis = _build_contract_analysis(record)

    assert analysis["document_id"] == "doc-1"
    assert analysis["risk_score"] > 0
    assert analysis["risk_level"] in {"medium", "high", "critical"}
    assert isinstance(analysis["missing_clauses"], list)


def test_signature_verification_detects_file_change(tmp_path: Path):
    record = _record(tmp_path)
    signature = _build_signature_payload(record, "user-1", "Test User", "test@example.com")
    record["signature"] = signature

    verified = _verify_signature_payload(record)
    assert verified["is_verified"] is True

    Path(record["file_path"]).write_text("tampered", encoding="utf-8")
    tampered = _verify_signature_payload(record)
    assert tampered["is_verified"] is False


def test_compliance_payload_returns_expected_shape(tmp_path: Path):
    record = _record(tmp_path)
    compliance = _build_compliance_payload(record)

    assert compliance["success"] is True
    assert compliance["documentId"] == "doc-1"
    assert isinstance(compliance["results"], list)
    assert "complianceScore" in compliance
