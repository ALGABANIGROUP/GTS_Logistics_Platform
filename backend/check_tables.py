from dotenv import load_dotenv
load_dotenv(".env")

import os
from sqlalchemy import create_engine, text

engine = create_engine(os.getenv("DATABASE_URL"))

sql = """
select tablename
from pg_tables
where schemaname='public'
and tablename in (
  'mailboxes','mailbox_credentials','email_threads','email_messages',
  'email_attachments','email_audit_logs','mailbox_requests'
)
order by tablename
"""

with engine.connect() as conn:
    rows = conn.execute(text(sql)).fetchall()
    print([r[0] for r in rows])
