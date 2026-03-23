#!/bin/bash
# Cron job setup for automated database backups
# Run this script once to setup automated backups

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_SCRIPT="$SCRIPT_DIR/backup_database.py"

echo "=========================================="
echo "GTS Database Backup - Cron Setup"
echo "=========================================="
echo ""
echo "Project Directory: $PROJECT_DIR"
echo "Backup Script: $BACKUP_SCRIPT"
echo ""

# Check if backup script exists
if [ ! -f "$BACKUP_SCRIPT" ]; then
    echo "❌ Error: Backup script not found at $BACKUP_SCRIPT"
    exit 1
fi

# Make script executable
chmod +x "$BACKUP_SCRIPT"
echo "✅ Made backup script executable"

# Backup schedule options
echo ""
echo "Select backup schedule:"
echo "1) Daily at 2:00 AM"
echo "2) Twice daily (2:00 AM and 2:00 PM)"
echo "3) Every 6 hours"
echo "4) Every 12 hours"
echo "5) Custom"
echo ""

read -p "Enter your choice (1-5): " schedule_choice

case $schedule_choice in
    1)
        CRON_SCHEDULE="0 2 * * *"
        CRON_DESC="Daily at 2:00 AM"
        ;;
    2)
        CRON_SCHEDULE="0 2,14 * * *"
        CRON_DESC="Twice daily at 2:00 AM and 2:00 PM"
        ;;
    3)
        CRON_SCHEDULE="0 */6 * * *"
        CRON_DESC="Every 6 hours"
        ;;
    4)
        CRON_SCHEDULE="0 */12 * * *"
        CRON_DESC="Every 12 hours"
        ;;
    5)
        read -p "Enter cron schedule (e.g., '0 3 * * *'): " CRON_SCHEDULE
        CRON_DESC="Custom: $CRON_SCHEDULE"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

# Create cron job entry
CRON_JOB="$CRON_SCHEDULE cd $PROJECT_DIR && $BACKUP_SCRIPT >> $PROJECT_DIR/backups/backup_cron.log 2>&1"

echo ""
echo "Cron job to be added:"
echo "----------------------------------------"
echo "Schedule: $CRON_DESC"
echo "Command: $CRON_JOB"
echo "----------------------------------------"
echo ""

read -p "Add this cron job? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "Cancelled"
    exit 0
fi

# Add cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Cron job added successfully!"
    echo ""
    echo "Current crontab:"
    crontab -l | grep backup_database.py
    echo ""
    echo "📝 Notes:"
    echo "- Backups will be saved to: $PROJECT_DIR/backups/"
    echo "- Logs will be saved to: $PROJECT_DIR/backups/backup_cron.log"
    echo "- Old backups are automatically cleaned up (30 days retention)"
    echo ""
    echo "To remove this cron job later, run:"
    echo "  crontab -e"
    echo "  (then delete the backup line)"
else
    echo "❌ Failed to add cron job"
    exit 1
fi
