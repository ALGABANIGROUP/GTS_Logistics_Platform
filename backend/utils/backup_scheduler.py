"""
Automated Database Backup System
Schedules backups based on platform technical settings.
"""

import asyncio
import logging
import os
import shutil
import subprocess
from datetime import datetime, timedelta
from typing import Optional, Tuple
from urllib.parse import urlparse, unquote

logger = logging.getLogger(__name__)

# Global backup task
_backup_task: Optional[asyncio.Task] = None


async def start_backup_scheduler():
    """
    Start the backup scheduler as a background task.
    Reads backup frequency from technical settings.
    """
    global _backup_task
    
    if _backup_task is not None:
        logger.warning("Backup scheduler already running")
        return
    
    _backup_task = asyncio.create_task(_backup_loop())
    logger.info("Backup scheduler started")


async def stop_backup_scheduler():
    """Stop the backup scheduler"""
    global _backup_task
    
    if _backup_task is None:
        return
    
    _backup_task.cancel()
    try:
        await _backup_task
    except asyncio.CancelledError:
        pass
    
    _backup_task = None
    logger.info("Backup scheduler stopped")


async def _backup_loop():
    """Main backup loop - runs continuously"""
    while True:
        try:
            # Refresh cached settings periodically
            try:
                from backend.database.session import get_async_session
                from backend.utils.technical_settings import get_technical_settings

                async for db in get_async_session():
                    await get_technical_settings(db)
                    break
            except Exception as refresh_error:
                logger.warning("Settings refresh failed: %s", refresh_error)

            from backend.utils.technical_settings import (
                get_backup_frequency_sync,
                get_database_settings_sync,
            )
            frequency = get_backup_frequency_sync()
            db_settings = get_database_settings_sync()
            backup_window = str(db_settings.get("backupWindow") or "").strip()

            next_run = _get_next_run_time(frequency, backup_window)
            sleep_seconds = max(0, int((next_run - datetime.now()).total_seconds()))

            logger.info(
                "Next backup scheduled at %s (frequency: %s)",
                next_run.strftime("%Y-%m-%d %H:%M:%S"),
                frequency,
            )

            await asyncio.sleep(sleep_seconds)
            await perform_backup()
            
        except asyncio.CancelledError:
            logger.info("Backup scheduler cancelled")
            break
        except Exception as e:
            logger.error(f"Backup scheduler error: {e}")
            # Wait 1 hour before retrying on error
            await asyncio.sleep(3600)


def _parse_backup_window(value: str) -> Optional[Tuple[int, int]]:
    """Parse HH:MM into hour/minute tuple."""
    if not value:
        return None
    parts = value.split(":")
    if len(parts) != 2:
        return None
    try:
        hour = int(parts[0])
        minute = int(parts[1])
    except ValueError:
        return None
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        return None
    return hour, minute


def _get_next_run_time(frequency: str, backup_window: str) -> datetime:
    """Calculate next backup time using frequency and optional window."""
    frequency = (frequency or "daily").lower()
    now = datetime.now()
    window = _parse_backup_window(backup_window)

    if frequency == "hourly":
        if window:
            target = now.replace(minute=window[1], second=0, microsecond=0)
            if target <= now:
                target = target + timedelta(hours=1)
            return target
        return now + timedelta(hours=1)

    if frequency in ("daily", "weekly", "monthly"):
        if window:
            target = now.replace(hour=window[0], minute=window[1], second=0, microsecond=0)
        else:
            target = now.replace(second=0, microsecond=0)

        if frequency == "daily":
            if target <= now:
                target = target + timedelta(days=1)
            return target

        if frequency == "weekly":
            if target <= now:
                target = target + timedelta(days=7)
            return target

        # monthly
        if target <= now:
            year = target.year + (1 if target.month == 12 else 0)
            month = 1 if target.month == 12 else target.month + 1
            day = min(target.day, _days_in_month(year, month))
            target = target.replace(year=year, month=month, day=day)
        return target

    logger.warning("Unknown backup frequency: %s, defaulting to daily", frequency)
    return now + timedelta(days=1)


def _days_in_month(year: int, month: int) -> int:
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    return (next_month - timedelta(days=1)).day


def _resolve_backup_dir() -> str:
    base_dir = os.getenv("BACKUP_DIR")
    if base_dir:
        return base_dir
    return os.path.join(os.getcwd(), "backups")


def _get_pg_dump_path() -> Optional[str]:
    configured = os.getenv("PG_DUMP_PATH")
    if configured:
        return configured
    return shutil.which("pg_dump")


def _parse_postgres_url(db_url: str) -> Optional[dict]:
    parsed = urlparse(db_url)
    scheme = (parsed.scheme or "").split("+")[0].lower()
    if not scheme.startswith("postgres"):
        return None
    dbname = (parsed.path or "").lstrip("/")
    if not dbname:
        return None
    return {
        "user": unquote(parsed.username or ""),
        "password": unquote(parsed.password or ""),
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 5432,
        "dbname": dbname,
    }


def _run_pg_dump(db_url: str, backup_path: str) -> Tuple[bool, str]:
    info = _parse_postgres_url(db_url)
    if not info:
        return False, "Unsupported database URL for pg_dump"

    pg_dump = _get_pg_dump_path()
    if not pg_dump:
        return False, "pg_dump not found in PATH (set PG_DUMP_PATH)"

    cmd = [
        pg_dump,
        "--no-owner",
        "--no-privileges",
        "-h",
        info["host"],
        "-p",
        str(info["port"]),
    ]
    if info["user"]:
        cmd.extend(["-U", info["user"]])
    cmd.extend(["-f", backup_path, info["dbname"]])

    env = os.environ.copy()
    if info["password"]:
        env["PGPASSWORD"] = info["password"]

    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "pg_dump failed").strip()
        return False, detail[:400]
    return True, "pg_dump completed"


def _prune_old_backups(backup_dir: str, retention_days: int) -> None:
    if retention_days <= 0:
        return
    cutoff = datetime.now() - timedelta(days=retention_days)
    try:
        for name in os.listdir(backup_dir):
            if not name.startswith("gts_backup_"):
                continue
            path = os.path.join(backup_dir, name)
            if not os.path.isfile(path):
                continue
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(path))
            except Exception:
                continue
            if mtime < cutoff:
                try:
                    os.remove(path)
                    logger.info("Removed old backup: %s", name)
                except Exception as exc:
                    logger.warning("Failed to remove old backup %s: %s", name, exc)
    except FileNotFoundError:
        return


async def perform_backup():
    """
    Perform database backup using pg_dump.
    Falls back to a scaffold file if pg_dump is not available.
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"gts_backup_{timestamp}.sql"
        
        logger.info(f"Starting database backup: {backup_filename}")
        
        # Get database URL
        db_url = os.getenv("DATABASE_URL") or os.getenv("ASYNC_DATABASE_URL")
        
        if not db_url:
            logger.error("Database URL not found, cannot perform backup")
            return
        
        backup_dir = _resolve_backup_dir()
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, backup_filename)

        ok, detail = await asyncio.to_thread(_run_pg_dump, db_url, backup_path)
        status = "success" if ok else "skipped"

        if not ok:
            with open(backup_path, "w", encoding="utf-8") as handle:
                handle.write("-- GTS backup scaffold
")
                handle.write(f"-- Timestamp: {timestamp}\n")
                handle.write(f"-- Reason: {detail}\n")
                handle.write("-- Install pg_dump or set PG_DUMP_PATH to enable real backups.\n")
            logger.warning("Backup scaffold created: %s", backup_path)
        else:
            logger.info("Backup completed: %s", backup_path)

        try:
            from backend.utils.technical_settings import get_database_settings_sync
            db_settings = get_database_settings_sync()
            retention_days = int(db_settings.get("backupRetentionDays", 14) or 14)
            _prune_old_backups(backup_dir, retention_days)
        except Exception as exc:
            logger.warning("Backup retention pruning failed: %s", exc)
        
        # Store backup metadata (could save to database or file)
        backup_record = {
            "timestamp": timestamp,
            "filename": backup_filename,
            "status": status,
            "note": detail
        }
        
        logger.info("Backup record: %s", backup_record)
        
    except Exception as e:
        logger.error(f"Backup failed: {e}")


async def trigger_manual_backup():
    """Manually trigger a backup (for admin endpoint)"""
    logger.info("Manual backup triggered")
    await perform_backup()
