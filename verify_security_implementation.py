#!/usr/bin/env python3
"""
Simple verification script for Session Revocation and Audit Logs implementation
"""
import asyncio
from backend.database.session import get_async_session
from sqlalchemy import text, select
from backend.models.user import User
from backend.models.audit_log import AuditLog

async def verify_implementation():
    async for session in get_async_session():
        try:
            print("🔍 Verifying Session Revocation and Audit Logs Implementation")
            print("=" * 60)

            # Check token_version column
            result = await session.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'token_version'
            """))
            column_info = result.fetchone()
            if column_info:
                print(f"✅ token_version column exists: {column_info}")
            else:
                print("❌ token_version column missing")

            # Check if auth_audit_logs table exists
            result = await session.execute(text("""
                SELECT table_name FROM information_schema.tables WHERE table_name = 'auth_audit_logs'
            """))
            if result.fetchone():
                print("✅ auth_audit_logs table exists")
            else:
                print("❌ auth_audit_logs table missing")

            # Check auth_audit_logs columns
            result = await session.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'auth_audit_logs'
                ORDER BY column_name
            """))
            columns = [row[0] for row in result.fetchall()]
            expected_columns = ['action', 'created_at', 'details', 'id', 'ip_address', 'user_agent', 'user_id']
            if set(columns) == set(expected_columns):
                print(f"✅ audit_logs columns correct: {columns}")
            else:
                print(f"❌ audit_logs columns mismatch. Expected: {expected_columns}, Got: {columns}")

            # Check indexes on auth_audit_logs
            result = await session.execute(text("""
                SELECT indexname FROM pg_indexes WHERE tablename = 'auth_audit_logs'
            """))
            indexes = [row[0] for row in result.fetchall()]
            print(f"✅ auth_audit_logs indexes: {indexes}")

            # Check sample user token_version
            result = await session.execute(select(User.id, User.email, User.token_version).limit(1))
            user = result.fetchone()
            if user:
                print(f"✅ Sample user token_version: {user}")

            # Check sample auth audit logs
            result = await session.execute(select(AuditLog).limit(3))
            logs = result.fetchall()
            if logs:
                print(f"✅ Sample auth audit logs: {len(logs)} entries found")
                for log in logs:
                    print(f"   - {log.action} by user {log.user_id} at {log.created_at}")
            else:
                print("ℹ️  No auth audit logs yet (expected if no auth events occurred)")

            print("\n🎉 Implementation verification complete!")

        except Exception as e:
            print(f"❌ Error during verification: {e}")
        finally:
            break

if __name__ == "__main__":
    asyncio.run(verify_implementation())