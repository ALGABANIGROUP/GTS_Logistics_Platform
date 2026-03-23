import os

def get_credentials():
    return {
        "imap_server": "mail.gabanilogistics.com",
        "email_account": "safety@gabanilogistics.com",
        "email_password": os.getenv("EMAIL_PASSWORD")
    }
