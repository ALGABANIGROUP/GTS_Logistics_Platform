import os

def get_credentials():
    return {
        "imap_server": "mail.gabanilogistics.com",
        "email_account": "finance@gabanilogistics.com",
        "email_password": os.getenv("EMAIL_PASSWORD")
    }
