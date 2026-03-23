import asyncio
from datetime import datetime, timedelta, timezone

from backend.bots.security_manager import SecurityManagerBot


def test_dashboard_contains_security_metrics() -> None:
    bot = SecurityManagerBot()
    result = asyncio.run(bot.run({"action": "dashboard"}))

    assert result["ok"] is True
    assert result["quick_stats"]["blocked_ips"] >= 1
    assert result["compliance"]["gdpr"] in {"compliant", "non_compliant"}


def test_process_message_routes_intrusion_analysis() -> None:
    bot = SecurityManagerBot()
    result = asyncio.run(
        bot.process_message(
            "Analyze this request for SQL injection from 45.123.45.67"
        )
    )

    assert result["ok"] is True
    assert result["has_threats"] is True
    assert any(item["type"] in {"sql_injection", "malicious_ip"} for item in result["threats"])


def test_encryption_and_session_actions_work() -> None:
    bot = SecurityManagerBot()

    encrypted = asyncio.run(
        bot.run(
            {
                "context": {
                    "action": "encrypt_sensitive_data",
                    "data": "top secret",
                    "purpose": "customer_data",
                }
            }
        )
    )
    decrypted = asyncio.run(
        bot.run(
            {
                "context": {
                    "action": "decrypt_sensitive_data",
                    "encrypted_data": encrypted["encrypted_data"],
                    "key_id": encrypted["key_id"],
                }
            }
        )
    )
    session = asyncio.run(
        bot.run(
            {
                "context": {
                    "action": "create_session",
                    "user_id": "user-1",
                    "ip": "10.10.10.10",
                    "user_agent": "pytest",
                }
            }
        )
    )
    validated = asyncio.run(
        bot.run(
            {
                "context": {
                    "action": "validate_session",
                    "session_id": session["session_id"],
                    "ip": "10.10.10.10",
                }
            }
        )
    )

    assert encrypted["ok"] is True
    assert decrypted["decrypted_data"] == "top secret"
    assert validated["valid"] is True


def test_bruteforce_and_ddos_detection() -> None:
    bot = SecurityManagerBot()
    now = datetime.now(timezone.utc)
    attempts = [
        {
            "ip_address": "45.123.45.67",
            "attempt_time": (now - timedelta(seconds=idx * 20)).isoformat(),
            "success": False,
        }
        for idx in range(5)
    ]
    traffic = [
        {
            "timestamp": (now - timedelta(seconds=1) + timedelta(milliseconds=idx * 5)).isoformat(),
            "ip": f"10.0.0.{idx}",
            "user_agent": "load-tester",
        }
        for idx in range(120)
    ]

    brute_force = asyncio.run(bot.detect_brute_force(attempts))
    ddos = asyncio.run(bot.detect_ddos(traffic))

    assert brute_force["is_brute_force"] is True
    assert ddos["is_ddos"] is True
