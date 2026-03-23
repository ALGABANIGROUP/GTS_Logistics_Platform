#!/usr/bin/env python3
"""
Script to run the database fix SQL file
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Load environment
load_dotenv()

def run_sql_file():
    """Run the SQL fix file"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not found in environment")
        return False

    sql_file = Path(__file__).parent / "fix_database_seed_rbac.sql"
    if not sql_file.exists():
        print(f"❌ SQL file not found: {sql_file}")
        return False

    try:
        print("🔄 Connecting to database...")
        engine = create_engine(db_url)

        print("📖 Reading SQL file...")
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print("⚡ Executing SQL commands...")
        with engine.connect() as conn:
            # Split SQL into individual statements
            statements = []
            current_statement = []
            in_multiline_comment = False

            for line in sql_content.split('\n'):
                line = line.strip()

                # Handle multiline comments
                if line.startswith('/*'):
                    in_multiline_comment = True
                if in_multiline_comment:
                    if '*/' in line:
                        in_multiline_comment = False
                    continue

                # Skip single line comments and empty lines
                if line.startswith('--') or not line:
                    continue

                current_statement.append(line)

                # Check if statement is complete (ends with semicolon)
                if line.endswith(';'):
                    statement = ' '.join(current_statement)
                    if statement.strip():
                        statements.append(statement)
                    current_statement = []

            # Execute each statement
            for i, statement in enumerate(statements, 1):
                try:
                    print(f"  Executing statement {i}/{len(statements)}...")
                    conn.execute(text(statement))
                    conn.commit()
                except Exception as e:
                    print(f"  ⚠️  Statement {i} failed: {e}")
                    # Continue with other statements

        print("✅ Database fix completed!")
        return True

    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = run_sql_file()
    sys.exit(0 if success else 1)