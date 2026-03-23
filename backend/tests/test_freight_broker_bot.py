import asyncio

from backend.bots.freight_broker import FreightBrokerBot


def test_dashboard_contains_broker_sections() -> None:
    bot = FreightBrokerBot()
    result = asyncio.run(bot.run({"action": "dashboard"}))

    assert result["ok"] is True
    assert "overview" in result
    assert "shipments" in result
    assert "top_carriers" in result
    assert result["overview"]["active_carriers"] >= 3


def test_process_message_dispatches_context_action() -> None:
    bot = FreightBrokerBot()
    result = asyncio.run(
        bot.process_message(
            "compare rates",
            {"action": "compare_rates", "origin": "Riyadh", "destination": "Jeddah", "weight": 500},
        )
    )

    assert result["ok"] is True
    assert result["origin"] == "Riyadh"
    assert len(result["offers"]) >= 3


def test_assign_carrier_updates_shipment_state() -> None:
    bot = FreightBrokerBot()
    result = asyncio.run(
        bot.run(
            {
                "context": {
                    "action": "assign_carrier",
                    "shipment_id": 103,
                    "carrier_id": 1,
                    "quoted_price": 1450,
                }
            }
        )
    )

    assert result["ok"] is True
    assert result["shipment"]["assigned_carrier_id"] == 1
    assert result["shipment"]["tracking_status"] == "booked"
