import pytest

from backend.email_service.intelligent_processor import IntelligentEmailProcessor
from backend.email_service.intelligent_router import IntelligentEmailRouter


@pytest.mark.parametrize(
    "to_email,expected_bot",
    [
        ("accounts@gabanilogistics.com", "finance_bot"),
        ("customers@gabanilogistics.com", "customer_service"),
        ("freight@gabanilogistics.com", "freight_broker"),
        ("doccontrol@gabanilogistics.com", "documents_manager"),
        ("driver@gabanilogistics.com", "operations_manager"),
        ("safety@gabanilogistics.com", "safety_manager"),
        ("security@gabanilogistics.com", "security_manager"),
    ],
)
def test_processor_routing_by_recipient(to_email, expected_bot):
    processor = IntelligentEmailProcessor()
    email = {"to": to_email, "subject": "Test", "body": ""}
    result = processor.process_incoming_email(email)
    assert result["bot"] == expected_bot


def test_router_shipment_workflow():
    router = IntelligentEmailRouter()
    email = {"subject": "Need shipment quote", "body": "shipment and quote"}
    result = router.route_and_process(email)
    steps = [r["step"] for r in result.get("workflow", [])]
    assert "extract_shipment_details" in steps
    assert result["success"] is True
