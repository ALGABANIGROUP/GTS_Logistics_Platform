try:
    from backend.ai.email_bot import generate_reply
except Exception:

    def generate_reply(_body: str) -> str:
        return 'Auto-reply disabled (email_bot not available).'

def handle_email(email_body: str) -> str:
    return generate_reply(email_body)