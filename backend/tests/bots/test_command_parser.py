from backend.bots.command_parser import parse_command


def test_parse_empty_command():
    result = parse_command("")
    assert result["ok"] is False


def test_parse_json_command():
    payload = '{"bot":"finance","action":"summary","params":{"days":7}}'
    result = parse_command(payload)
    assert result["ok"] is True
    assert result["bot_name"] == "finance_bot"
    assert result["task_type"] == "summary"
    assert result["params"] == {"days": 7}


def test_parse_text_command():
    result = parse_command("run freight create")
    assert result["ok"] is True
    assert result["bot_name"] == "freight_broker"
    assert result["task_type"] == "create"


def test_parse_key_value_command():
    result = parse_command("bot: safety action: monitor")
    assert result["ok"] is True
    assert result["bot_name"] == "safety"
    assert result["task_type"] == "monitor"
