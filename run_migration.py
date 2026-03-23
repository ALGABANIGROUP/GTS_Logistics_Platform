#!/usr/bin/env python3
"""
Script to run database migrations for GTS
"""
import os
import sys
import subprocess

def run_migration():
    """Run alembic upgrade head"""
    try:
        # Change to backend directory
        backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
        os.chdir(backend_dir)

        # Run alembic upgrade
        result = subprocess.run([
            sys.executable, '-m', 'alembic', 'upgrade', 'head'
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print("✅ Migration completed successfully!")
            print(result.stdout)
        else:
            print("❌ Migration failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

    except Exception as e:
        print(f"❌ Error running migration: {e}")
        return False

    return True

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)