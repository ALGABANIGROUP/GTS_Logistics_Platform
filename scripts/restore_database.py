#!/usr/bin/env python3
"""
PostgreSQL Database Restore Script for GTS Platform
Restores database from backup with safety checks
"""
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import logging

# Configuration
BACKUP_DIR = Path(__file__).parent.parent / "backups"

# Database configuration from environment
DB_HOST = os.getenv("PG_HOST", "localhost")
DB_PORT = os.getenv("PG_PORT", "5432")
DB_NAME = os.getenv("PG_DB", "gts")
DB_USER = os.getenv("PG_USER", "postgres")
DB_PASSWORD = os.getenv("PG_PASSWORD", "")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def list_available_backups():
    """List all available backup files"""
    if not BACKUP_DIR.exists():
        print("❌ No backups directory found")
        return []
    
    backups = sorted(
        BACKUP_DIR.glob("gts_backup_*.sql.gz"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    
    if not backups:
        print("❌ No backup files found")
        return []
    
    print(f"\n{'='*70}")
    print(f"Available Backups ({len(backups)} total)")
    print(f"{'='*70}")
    print(f"{'#':<5} {'Filename':<40} {'Size (MB)':<12} {'Date':<20}")
    print(f"{'-'*70}")
    
    for idx, backup in enumerate(backups, 1):
        size_mb = backup.stat().st_size / (1024 * 1024)
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        print(f"{idx:<5} {backup.name:<40} {size_mb:>10.2f}  {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"{'='*70}\n")
    return backups


def confirm_restore():
    """Ask user to confirm restore operation"""
    print("\n" + "="*70)
    print("⚠️  WARNING: DATABASE RESTORE OPERATION")
    print("="*70)
    print("This will OVERWRITE the current database with backup data.")
    print("All current data will be LOST if not backed up.")
    print("="*70)
    
    response = input("\nType 'YES' to continue with restore: ")
    return response.strip().upper() == "YES"


def restore_from_backup(backup_file: Path):
    """Restore database from backup file"""
    logger.info(f"Starting restore from {backup_file}")
    
    try:
        # Set PostgreSQL password environment variable
        env = os.environ.copy()
        env['PGPASSWORD'] = DB_PASSWORD
        
        # Decompress backup file temporarily
        temp_file = backup_file.with_suffix("")  # Remove .gz extension
        logger.info(f"Decompressing backup file...")
        
        decompress_cmd = ["gunzip", "-k", str(backup_file)]  # -k keeps original
        subprocess.run(decompress_cmd, check=True)
        
        # Drop existing database (if exists) and recreate
        logger.info(f"Preparing database for restore...")
        
        # Terminate existing connections
        terminate_cmd = [
            "psql",
            "-h", DB_HOST,
            "-p", DB_PORT,
            "-U", DB_USER,
            "-d", "postgres",
            "-c", f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{DB_NAME}';"
        ]
        subprocess.run(terminate_cmd, env=env, capture_output=True)
        
        # Drop and recreate database
        drop_cmd = [
            "psql",
            "-h", DB_HOST,
            "-p", DB_PORT,
            "-U", DB_USER,
            "-d", "postgres",
            "-c", f"DROP DATABASE IF EXISTS {DB_NAME};"
        ]
        subprocess.run(drop_cmd, env=env, check=True)
        
        create_cmd = [
            "psql",
            "-h", DB_HOST,
            "-p", DB_PORT,
            "-U", DB_USER,
            "-d", "postgres",
            "-c", f"CREATE DATABASE {DB_NAME};"
        ]
        subprocess.run(create_cmd, env=env, check=True)
        
        # Restore from backup
        logger.info(f"Restoring database from backup...")
        restore_cmd = [
            "psql",
            "-h", DB_HOST,
            "-p", DB_PORT,
            "-U", DB_USER,
            "-d", DB_NAME,
            "-f", str(temp_file),
            "--quiet"
        ]
        
        result = subprocess.run(
            restore_cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        # Clean up temporary file
        temp_file.unlink()
        
        if result.returncode != 0:
            error_msg = result.stderr
            logger.error(f"Restore failed: {error_msg}")
            return False
        
        logger.info(f"✅ Database restored successfully from {backup_file.name}")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error("Restore timeout after 1 hour")
        return False
    except Exception as e:
        logger.error(f"Restore error: {e}")
        return False


def main():
    """Main restore execution"""
    logger.info("="*50)
    logger.info("GTS Database Restore Utility")
    logger.info(f"Database: {DB_NAME}@{DB_HOST}:{DB_PORT}")
    logger.info("="*50)
    
    # List available backups
    backups = list_available_backups()
    if not backups:
        sys.exit(1)
    
    # Get user selection
    try:
        selection = input("\nEnter backup number to restore (or 'q' to quit): ").strip()
        
        if selection.lower() == 'q':
            print("Restore cancelled")
            sys.exit(0)
        
        idx = int(selection) - 1
        if idx < 0 or idx >= len(backups):
            print("❌ Invalid selection")
            sys.exit(1)
        
        selected_backup = backups[idx]
        
    except ValueError:
        print("❌ Invalid input")
        sys.exit(1)
    
    # Confirm restore operation
    if not confirm_restore():
        print("Restore cancelled by user")
        sys.exit(0)
    
    # Perform restore
    print(f"\n🔄 Restoring from: {selected_backup.name}")
    success = restore_from_backup(selected_backup)
    
    if success:
        print("\n✅ Database restore completed successfully!")
        print("\n⚠️  IMPORTANT: Restart your application to use the restored database")
    else:
        print("\n❌ Database restore failed - check logs for details")
        sys.exit(1)


if __name__ == "__main__":
    main()
