from backend.utils.email_utils import send_email


def send_email_reminder(to_email, message):
    return send_email(
        subject="Document Expiry Reminder",
        body=message,
        to=[to_email],
        html=False,
    )
