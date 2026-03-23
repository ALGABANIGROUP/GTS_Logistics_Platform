import asyncio

from backend.bots.mapleload_canada import MapleLoadCanadaBot


def test_dashboard_contains_international_signals() -> None:
    bot = MapleLoadCanadaBot()
    dashboard = asyncio.run(bot.run({"action": "dashboard"}))

    assert dashboard["ok"] is True
    assert "overview" in dashboard
    assert "shipping" in dashboard
    assert "expansion" in dashboard


def test_process_message_dispatches_context_action() -> None:
    bot = MapleLoadCanadaBot()

    result = asyncio.run(
        bot.process_message(
            "quote this shipment",
            {
                "action": "dynamic_pricing",
                "origin_country": "CA",
                "destination_country": "US",
                "weight": 25,
                "is_peak": True,
            },
        )
    )

    assert result["ok"] is True
    assert result["pricing"]["destination"] == "US"
    assert result["pricing"]["total_price"] > 0


def test_market_expansion_action_returns_feasibility() -> None:
    bot = MapleLoadCanadaBot()
    result = asyncio.run(
        bot.run({"context": {"action": "market_expansion", "country_code": "AE"}})
    )

    assert result["ok"] is True
    assert result["market_expansion"]["country"] == "AE"
    assert result["market_expansion"]["feasibility_score"] >= 70
