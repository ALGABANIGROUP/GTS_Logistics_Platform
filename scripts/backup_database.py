#!/usr/bin/env python3
"""
PostgreSQL Database Backup Script for GTS Platform
Performs automated backups with retention policy
"""
import os
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Configuration
BACKUP_DIR = Path(__file__).parent.parent / "backups"
RETENTION_DAYS = 30  # Keep backups for 30 days
MAX_BACKUPS = 50  # Maximum number of backups to keep

# Database configuration from environment
DB_HOST = os.getenv("PG_HOST", "localhost")
DB_PORT = os.getenv("PG_PORT", "5432")
DB_NAME = os.getenv("PG_DB", "gts")
DB_USER = os.getenv("PG_USER", "postgres")
DB_PASSWORD = os.getenv("PG_PASSWORD", "")

# Email configuration for alerts
ALERT_EMAIL = os.getenv("ADMIN_EMAIL", "")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(BACKUP_DIR / "backup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def send_alert_email(subject: str, body: str):
    """Send alert email to administrator"""
    if not all([ALERT_EMAIL, SMTP_HOST, SMTP_USER, SMTP_PASSWORD]):
        logger.warning("Email configuration incomplete, skipping alert")
        return
    
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = ALERT_EMAIL
        msg['Subject'] = f"[GTS Backup] {subject}"
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP_SSL(SMTP_HOST, 465) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Alert email sent to {ALERT_EMAIL}")
    except Exception as e:
        logger.error(f"Failed to send alert email: {e}")


def create_backup():
    """Create database backup using pg_dump"""
    # Create backup directory if it doesn't exist
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"gts_backup_{timestamp}.sql"
    compressed_file = BACKUP_DIR / f"gts_backup_{timestamp}.sql.gz"
    
    logger.info(f"Starting backup to {backup_file}")
    
    try:
        # Set PostgreSQL password environment variable
        env = os.environ.copy()
        env['PGPASSWORD'] = DB_PASSWORD
        
        # Run pg_dump command
        cmd = [
            "pg_dump",
            "-h", DB_HOST,
            "-p", DB_PORT,
            "-U", DB_USER,
            "-d", DB_NAME,
            "-F", "p",  # Plain text format
            "-f", str(backup_file),
            "--verbose"
        ]
        
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        if result.returncode != 0:
            error_msg = result.stderr
            logger.error(f"Backup failed: {error_msg}")
            send_alert_email(
                "❌ Backup Failed",
                f"Database backup failed at {datetime.now()}\n\nError:\n{error_msg}"
            )
            return False
        
        # Compress backup file
        logger.info(f"Compressing backup file...")
        compress_cmd = ["gzip", str(backup_file)]
        subprocess.run(compress_cmd, check=True)
        
        # Get file size
        file_size_mb = compressed_file.stat().st_size / (1024 * 1024)
        logger.info(f"✅ Backup completed successfully: {compressed_file} ({file_size_mb:.2f} MB)")
        
        # Send success notification
        send_alert_email(
            "✅ Backup Successful",
            f"Database backup completed successfully\n\n"
            f"File: {compressed_file.name}\n"
            f"Size: {file_size_mb:.2f} MB\n"
            f"Time: {datetime.now()}\n"
            f"Database: {DB_NAME}@{DB_HOST}"
        )
        
        return True
        
    except subprocess.TimeoutExpired:
        logger.error("Backup timeout after 1 hour")
        send_alert_email("❌ Backup Timeout", "Database backup exceeded 1 hour timeout")
        return False
    except Exception as e:
        logger.error(f"Backup error: {e}")
        send_alert_email("❌ Backup Error", f"Unexpected error during backup:\n\n{str(e)}")
        return False


def cleanup_old_backups():
    """Remove backups older than retention period"""
    logger.info(f"Cleaning up backups older than {RETENTION_DAYS} days...")
    
    if not BACKUP_DIR.exists():
        return
    
    cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)
    removed_count = 0
    
    for backup_file in BACKUP_DIR.glob("gts_backup_*.sql.gz"):
        # Extract timestamp from filename
        try:
            timestamp_str = backup_file.stem.replace("gts_backup_", "").replace(".sql", "")
            file_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            
            if file_date < cutoff_date:
                backup_file.unlink()
                removed_count += 1
                logger.info(f"Removed old backup: {backup_file.name}")
        except Exception as e:
            logger.warning(f"Could not process file {backup_file}: {e}")
    
    # Also enforce maximum backup count
    all_backups = sorted(BACKUP_DIR.glob("gts_backup_*.sql.gz"), key=lambda x: x.stat().st_mtime, reverse=True)
    if len(all_backups) > MAX_BACKUPS:
        for old_backup in all_backups[MAX_BACKUPS:]:
            old_backup.unlink()
            removed_count += 1
            logger.info(f"Removed excess backup: {old_backup.name}")
    
    logger.info(f"Cleanup completed: {removed_count} files removed")


def verify_backup_integrity(backup_file: Path):
    """Verify backup file is not corrupted"""
    try:
        # Test gzip integrity
        result = subprocess.run(
            ["gzip", "-t", str(backup_file)],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Backup verification failed: {e}")
        return False


def list_backups():
    """List all available backups"""
    if not BACKUP_DIR.exists():
        print("No backups directory found")
        return
    
    backups = sorted(BACKUP_DIR.glob("gts_backup_*.sql.gz"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not backups:
        print("No backups found")
        return
    
    print(f"\n{'='*70}")
    print(f"Available Backups ({len(backups)} total)")
    print(f"{'='*70}")
    print(f"{'Filename':<40} {'Size (MB)':<12} {'Date':<20}")
    print(f"{'-'*70}")
    
    for backup in backups:
        size_mb = backup.stat().st_size / (1024 * 1024)
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        print(f"{backup.name:<40} {size_mb:>10.2f}  {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"{'='*70}\n")


def main():
    """Main backup execution"""
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_backups()
        return
    
    logger.info("="*50)
    logger.info("GTS Database Backup Starting")
    logger.info(f"Database: {DB_NAME}@{DB_HOST}:{DB_PORT}")
    logger.info(f"Backup Directory: {BACKUP_DIR}")
    logger.info("="*50)
    
    # Perform backup
    success = create_backup()
    
    if success:
        # Cleanup old backups
        cleanup_old_backups()
        logger.info("✅ Backup process completed successfully")
    else:
        logger.error("❌ Backup process failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
