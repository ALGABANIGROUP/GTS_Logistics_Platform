import asyncio

from backend.bots.sales_intelligence import SalesIntelligenceBot


def test_dashboard_contains_sales_signals() -> None:
    bot = SalesIntelligenceBot()
    dashboard = asyncio.run(bot.run({"action": "dashboard"}))

    assert dashboard["ok"] is True
    assert dashboard["stats"]["totalLeads"] >= 3
    assert dashboard["stats"]["totalDeals"] >= 3
    assert "insights" in dashboard
    assert "pricing" in dashboard["insights"]


def test_process_message_dispatches_context_action() -> None:
    bot = SalesIntelligenceBot()

    created = asyncio.run(
        bot.process_message(
            "create lead",
            {
                "action": "create_lead",
                "data": {
                    "name": "New Growth Account",
                    "contact": "Ava Stone",
                    "email": "ava@example.com",
                    "phone": "+1-555-0200",
                    "source": "Website",
                    "value": 56000,
                },
            },
        )
    )
    leads = asyncio.run(bot.get_leads())

    assert created["ok"] is True
    assert created["lead"]["name"] == "New Growth Account"
    assert any(lead["name"] == "New Growth Account" for lead in leads["leads"])


def test_deal_updates_are_persisted() -> None:
    bot = SalesIntelligenceBot()
    deal = asyncio.run(
        bot.create_deal(
            {
                "customer": "Expansion Freight",
                "value": 72000,
                "stage": "DISCOVERY",
                "probability": 45,
            }
        )
    )

    updated = asyncio.run(bot.update_deal(deal["deal"]["id"], "PROPOSAL"))

    assert updated["ok"] is True
    assert updated["deal"]["stage"] == "PROPOSAL"
