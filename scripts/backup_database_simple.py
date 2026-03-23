#!/usr/bin/env python3
"""
GTS Database Backup (Windows-Compatible Version using psycopg)
Performs automated backups with compression
"""
import os
import sys
import gzip
from datetime import datetime
from pathlib import Path
import logging

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Setup backup directory
BACKUP_DIR = Path(__file__).parent.parent / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(BACKUP_DIR / "backup.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def create_backup_simple():
    """Create backup using SQL queries (works on Windows)"""
    try:
        import psycopg
        
        logger.info("=" * 60)
        logger.info("Starting GTS Database Backup")
        
        # Get database URL
        db_url = os.getenv("DATABASE_URL") or os.getenv("ASYNC_DATABASE_URL", "")
        db_url = db_url.replace("+asyncpg", "")
        
        if not db_url:
            logger.error("ERROR: DATABASE_URL or ASYNC_DATABASE_URL not set")
            return False
        
        logger.info(f"Connecting to database...")
        
        # Create backup file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_DIR / f"gts_backup_{timestamp}.sql"
        compressed_file = BACKUP_DIR / f"gts_backup_{timestamp}.sql.gz"
        
        sql_lines = []
        sql_lines.append("-- GTS Database Backup")
        sql_lines.append(f"-- Created: {datetime.now().isoformat()}")
        sql_lines.append("")
        
        # Connect and dump
        with psycopg.connect(db_url) as conn:
            with conn.cursor() as cur:
                # Get all tables
                cur.execute("""
                    SELECT schemaname, tablename 
                    FROM pg_tables 
                    WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                    ORDER BY schemaname, tablename
                """)
                tables = cur.fetchall()
                logger.info(f"Found {len(tables)} tables")
        
                # Dump each table
                for schema, table in tables:
                    full_table = f"{schema}.{table}"
                    try:
                        sql_lines.append(f"\n-- Table: {full_table}")
                        sql_lines.append(f"DROP TABLE IF EXISTS {full_table} CASCADE;")
                        
                        # Get CREATE TABLE statement
                        cur.execute(f"""
                            SELECT pg_get_ddl('"{schema}"."{table}"'::regclass::oid)
                        """)
                        ddl = cur.fetchone()
                        if ddl and ddl[0]:
                            sql_lines.append(ddl[0] + ";")
                        
                        # Get data
                        cur.execute(f"SELECT * FROM {full_table}")
                        rows = cur.fetchall()
                        if rows:
                            # Get column names
                            col_names = [desc.name for desc in cur.description]
                            for row in rows:
                                values = ", ".join(
                                    "NULL" if v is None else f"'{str(v).replace(chr(39), chr(39)*2)}'" 
                                    for v in row
                                )
                                sql_lines.append(f"INSERT INTO {full_table} ({', '.join(col_names)}) VALUES ({values});")
                    except Exception as e:
                        logger.warning(f"Warning dumping {full_table}: {e}")
                        continue
        
        # Write SQL file
        sql_content = "\n".join(sql_lines)
        with open(backup_file, "w", encoding="utf-8") as f:
            f.write(sql_content)
        
        logger.info(f"SQL file created: {backup_file.name}")
        
        # Compress
        logger.info("Compressing backup...")
        with open(backup_file, "rb") as f_in:
            with gzip.open(compressed_file, "wb") as f_out:
                f_out.write(f_in.read())
        
        backup_file.unlink()
        
        # Verify
        size_mb = compressed_file.stat().st_size / (1024 * 1024)
        logger.info(f"SUCCESS: Backup created: {compressed_file.name}")
        logger.info(f"Size: {size_mb:.2f} MB")
        logger.info("=" * 60)
        
        return True
        
    except ImportError:
        logger.error("ERROR: psycopg not installed")
        logger.error("Install with: pip install psycopg[binary]")
        return False
    except Exception as e:
        logger.error(f"ERROR: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def list_backups():
    """List all available backups"""
    backups = sorted(BACKUP_DIR.glob("gts_backup_*.sql.gz"))
    if not backups:
        print("No backups found")
        return
    
    print("\nAvailable Backups:")
    print("-" * 60)
    for i, backup in enumerate(backups, 1):
        size_mb = backup.stat().st_size / (1024 * 1024)
        mtime = backup.stat().st_mtime
        from_epoch = datetime.fromtimestamp(mtime)
        print(f"{i}. {backup.name} ({size_mb:.2f} MB) - {from_epoch}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_backups()
    else:
        success = create_backup_simple()
        sys.exit(0 if success else 1)
