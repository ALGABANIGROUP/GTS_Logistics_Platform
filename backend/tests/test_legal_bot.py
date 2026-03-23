import asyncio

from backend.bots.legal_bot import LegalBot


def test_dashboard_contains_legal_library_stats() -> None:
    bot = LegalBot()
    result = asyncio.run(bot.run({"action": "dashboard"}))

    assert result["ok"] is True
    assert result["stats"]["total_laws"] >= 5
    assert result["coverage"]["international"] >= 1


def test_process_message_routes_contract_review() -> None:
    bot = LegalBot()
    result = asyncio.run(
        bot.process_message(
            "Please review this contract with unlimited liability and no force majeure clause."
        )
    )

    assert result["ok"] is True
    assert result["risk_level"] in {"high", "medium", "low"}
    assert any("Unlimited liability" in item["risk"] for item in result["risks"])


def test_liability_and_required_documents_actions_work() -> None:
    bot = LegalBot()
    liability = asyncio.run(
        bot.run(
            {
                "context": {
                    "action": "calculate_liability",
                    "law": "cmr_convention_1956",
                    "weight": 1000,
                    "value": 15000,
                    "damage_type": "damage",
                }
            }
        )
    )
    documents = asyncio.run(
        bot.run(
            {
                "context": {
                    "action": "required_documents",
                    "origin": "Canada",
                    "destination": "Saudi Arabia",
                    "goods_type": "electronics",
                }
            }
        )
    )

    assert liability["ok"] is True
    assert liability["law_applied"] == "cmr_convention_1956"
    assert documents["ok"] is True
    assert any(item["name"] == "Certificate of origin" for item in documents["documents"])
