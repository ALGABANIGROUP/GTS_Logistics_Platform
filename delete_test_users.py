from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/gts")
engine = create_engine(DATABASE_URL)

def delete_test_users():
    test_emails = [
        "test_fix2@example.com",
        "ps_test1@example.com",
        "ps_fix_register@example.com",
        "ps_scope_ok@example.com",
        "ps_contract_250196092@example.com",
        "ps_contract_1567261833@example.com",
        "ps_contract_204778719@example.com",
        "tester@gts.com",
        "test_%00null_byte@test.com",
        "system@local",
    ]

    with engine.connect() as connection:
        print(f"🔍 Searching for {len(test_emails)} users...\n")
        for email in test_emails:
            result = connection.execute(text("""
                SELECT id, email, first_name, role FROM users
                WHERE email = :email
            """), {"email": email})
            user = result.fetchone()
            if user:
                print(f"✅ Found: ID {user[0]} - {user[1]} ({user[3]})")
            else:
                print(f"❌ Not found: {email}")

        confirm = input("\nDo you want to delete these users? (yes/no): ")
        if confirm.lower() == "yes":
            deleted_count = 0
            for email in test_emails:
                result = connection.execute(text("""
                    DELETE FROM users
                    WHERE email = :email
                    RETURNING id, email
                """), {"email": email})
                deleted = result.fetchone()
                if deleted:
                    deleted_count += 1
                    print(f"🗑️ Deleted: {deleted[1]}")
            connection.commit()
            print(f"\n✅ Successfully deleted {deleted_count} users")
        else:
            print("❌ Cancelled")

if __name__ == "__main__":
    delete_test_users()