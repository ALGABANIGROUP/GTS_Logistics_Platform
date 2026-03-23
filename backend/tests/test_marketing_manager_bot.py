import asyncio

from backend.bots.marketing_manager import MarketingManagerBot


def test_dashboard_contains_marketing_sections() -> None:
    bot = MarketingManagerBot()
    result = asyncio.run(bot.run({"action": "dashboard"}))

    assert result["ok"] is True
    assert "campaigns" in result
    assert "leads" in result
    assert "today" in result


def test_process_message_routes_lead_analysis() -> None:
    bot = MarketingManagerBot()
    result = asyncio.run(bot.process_message("Analyze lead quality"))

    assert result["ok"] is True
    assert "total_leads" in result
    assert "by_status" in result


def test_campaign_creation_and_performance_analysis_work() -> None:
    bot = MarketingManagerBot()
    created = asyncio.run(
        bot.run(
            {
                "context": {
                    "action": "create_campaign",
                    "data": {
                        "name": "LinkedIn Enterprise Push",
                        "type": "social",
                        "channel": "LinkedIn",
                        "budget": 7500,
                        "goals": {"leads": 40},
                    },
                }
            }
        )
    )
    campaign_id = created["campaign"]["campaign_id"]
    performance = asyncio.run(
        bot.run(
            {
                "context": {
                    "action": "record_campaign_performance",
                    "campaign_id": campaign_id,
                    "metrics": {
                        "impressions": 10000,
                        "clicks": 250,
                        "conversions": 12,
                        "cost": 400,
                        "revenue": 1800,
                    },
                }
            }
        )
    )
    analysis = asyncio.run(bot.run({"context": {"action": "analyze_campaign", "campaign_id": campaign_id}}))

    assert created["ok"] is True
    assert performance["ok"] is True
    assert analysis["ok"] is True
    assert analysis["averages"]["roi"] > 0


def test_leads_segments_and_promotions_work() -> None:
    bot = MarketingManagerBot()
    lead = asyncio.run(
        bot.run(
            {
                "context": {
                    "action": "add_lead",
                    "data": {
                        "source_campaign": "CAMP001",
                        "source_channel": "Email",
                        "first_name": "Mona",
                        "last_name": "Rashid",
                        "email": "mona@enterprise.com",
                        "phone": "+971500000000",
                        "position": "Commercial Manager",
                    },
                }
            }
        )
    )
    segments = asyncio.run(bot.run({"context": {"action": "segment_customers"}}))
    promo = asyncio.run(
        bot.run(
            {
                "context": {
                    "action": "create_promotion",
                    "data": {"name": "VIP Offer", "type": "discount", "discount_value": 15, "target_segment": "high_value"},
                }
            }
        )
    )
    sent = asyncio.run(
        bot.run(
            {
                "context": {
                    "action": "send_promotion_to_segment",
                    "segment": "high_value",
                    "promo_id": promo["promotion"]["promo_id"],
                }
            }
        )
    )

    assert lead["ok"] is True
    assert lead["lead"]["lead_score"] >= 80
    assert segments["ok"] is True
    assert segments["segments"]["high_value"]["count"] >= 1
    assert promo["ok"] is True
    assert sent["ok"] is True
