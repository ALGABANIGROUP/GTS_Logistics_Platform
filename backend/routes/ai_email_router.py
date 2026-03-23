from fastapi import APIRouter, Depends
import sqlite3
from backend.utils.role_protected import RoleChecker
admin_or_manager_required = RoleChecker(['admin', 'manager'])
router = APIRouter(prefix='/ai-email', tags=['AI Email Assistant'], dependencies=[Depends(admin_or_manager_required)])

@router.get('/ping')
async def ping_ai_email():
    return {'message': 'AI Email Router is active.'}

@router.get('/logs')
async def get_email_logs():
    conn = sqlite3.connect('gts.db')
    cursor = conn.cursor()
    cursor.execute('SELECT bot, from_email, subject, reply, timestamp FROM email_logs ORDER BY id DESC LIMIT 50')
    rows = cursor.fetchall()
    conn.close()
    return [{'bot': row[0], 'from': row[1], 'subject': row[2], 'reply': row[3], 'timestamp': row[4]} for row in rows]

@router.get('/logs/latest')
async def get_latest_email_logs():
    conn = sqlite3.connect('gts.db')
    cursor = conn.cursor()
    cursor.execute('SELECT bot, from_email, subject, reply, timestamp FROM email_logs ORDER BY id DESC LIMIT 5')
    rows = cursor.fetchall()
    conn.close()
    return [{'bot': row[0], 'from': row[1], 'subject': row[2], 'reply': row[3], 'timestamp': row[4]} for row in rows]