Email System Overview
=====================

This project uses a DB-backed email system with scheduled polling. Mailboxes are provisioned from
the system bot mapping at startup, and credentials are stored encrypted at rest.

Environment variables
---------------------

Required:
- `EMAIL_SHARED_PASSWORD` or `EMAIL_PASSWORD`: shared password used for provisioning bot mailboxes.

Optional:
- `EMAIL_IMAP_HOST`: IMAP server hostname
- `EMAIL_SMTP_HOST`: SMTP server hostname
- `EMAIL_IMAP_PORT`: defaults to 993
- `EMAIL_SMTP_PORT`: defaults to 465
- `EMAIL_POLL_INTERVAL_SEC` or `EMAIL_POLLING_INTERVAL`: polling interval in seconds (default 300)
- `EMAIL_POLL_ENABLED`: set to `0` to disable polling

Notes:
- Passwords are never returned by API endpoints and are never logged.
- The no-reply mailbox is outbound-only and is never polled.

Operational flow
----------------

1) Startup provisions system mailboxes and credentials.
2) Poller reads enabled mailboxes and stores inbound messages.
3) The Email Center UI lists mailboxes and threads from the database.

Monitoring endpoint
-------------------

- `GET /api/v1/email/status` returns polling state and last cycle timestamp.
