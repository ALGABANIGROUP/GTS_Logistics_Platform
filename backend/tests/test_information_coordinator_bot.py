import asyncio

from backend.bots.information_coordinator import InformationCoordinatorBot


def test_dashboard_contains_coordination_sections() -> None:
    bot = InformationCoordinatorBot()
    result = asyncio.run(bot.run({"action": "dashboard"}))

    assert result["ok"] is True
    assert "overview" in result
    assert "source_health" in result
    assert "conflicts" in result
    assert result["overview"]["active_sources"] >= 4


def test_process_message_dispatches_context_action() -> None:
    bot = InformationCoordinatorBot()
    result = asyncio.run(
        bot.process_message(
            "resolve data conflict",
            {"action": "resolve_conflict", "conflict_id": "CONF001", "strategy": "source_reliability"},
        )
    )

    assert result["ok"] is True
    assert result["conflict"]["status"] == "resolved"
    assert result["strategy_used"] == "source_reliability"


def test_unified_entity_creation_merges_records() -> None:
    bot = InformationCoordinatorBot()
    result = asyncio.run(
        bot.run(
            {
                "context": {
                    "action": "unified_entity",
                    "entity_type": "customer",
                    "entity_id": "CUST900",
                    "records": [
                        {
                            "source": "SALES",
                            "data": {
                                "name": "North Star Logistics",
                                "email": "ops@northstar.test",
                                "tier": "silver",
                            },
                        },
                        {
                            "source": "CUSTOMER_SERVICE",
                            "data": {
                                "name": "North Star Logistics",
                                "email": "ops@northstar.test",
                                "phone": "+966500000123",
                            },
                        },
                    ],
                }
            }
        )
    )

    assert result["ok"] is True
    assert result["entity"]["entity_id"] == "CUST900"
    assert result["entity"]["data"]["name"] == "North Star Logistics"
    assert "CUSTOMER_SERVICE" in result["entity"]["sources_used"]


def test_receive_data_updates_entities_and_audit_log() -> None:
    bot = InformationCoordinatorBot()
    result = asyncio.run(
        bot.run(
            {
                "context": {
                    "action": "receive_data",
                    "source": "DISPATCHER",
                    "data": {
                        "shipment": {
                            "shipment_number": "SHP777",
                            "customer_id": "CUST001",
                            "origin_city": "Riyadh",
                            "destination_city": "Dammam",
                            "status": "booked",
                        }
                    },
                }
            }
        )
    )

    assert result["ok"] is True
    assert result["received"] is True
    assert any("shipment:SHP777" in item for item in result["entities_updated"])


def test_request_data_and_conflict_suggestions_work() -> None:
    bot = InformationCoordinatorBot()
    entity = asyncio.run(
        bot.run(
            {
                "context": {
                    "action": "request_data",
                    "entity_type": "customer",
                    "entity_id": "CUST001",
                    "fields": ["name", "phone"],
                }
            }
        )
    )
    suggestions = asyncio.run(
        bot.run(
            {
                "context": {
                    "action": "conflict_suggestions",
                    "conflict_id": "CONF001",
                }
            }
        )
    )

    assert entity["ok"] is True
    assert entity["found"] is True
    assert set(entity["data"].keys()) == {"name", "phone"}
    assert suggestions["ok"] is True
    assert len(suggestions["suggestions"]) >= 2
