#!/usr/bin/env python3
"""
Retention script for audit logs: keeps only the last N days (default: 180).
Usage:
    python clean_old_audit_logs.py [days]
"""
import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 180

db_url = os.getenv('DATABASE_URL') or os.getenv('ASYNC_DATABASE_URL')
if not db_url:
    print('No DB URL found')
    sys.exit(1)

engine = create_engine(db_url)
cutoff = datetime.utcnow() - timedelta(days=DAYS)

with engine.begin() as conn:
    result = conn.execute(text("""
        DELETE FROM auth_audit_logs WHERE created_at < :cutoff
    """), {"cutoff": cutoff})
    print(f"Deleted {result.rowcount} old audit log records (older than {DAYS} days)")
