from fastapi import APIRouter
import os, json
import aiofiles

router = APIRouter()

LOGS_DIR = "logs"

@router.get("/emails/logs")
async def get_all_email_logs():
    data = []
    if not os.path.exists(LOGS_DIR):
        return []
    for filename in os.listdir(LOGS_DIR):
        if filename.endswith("_email_log.json"):
            path = os.path.join(LOGS_DIR, filename)
            try:
                async with aiofiles.open(path, "r", encoding="utf-8") as f:
                    content = await f.read()
                    data.extend(json.loads(content))
            except Exception:
                continue
    sorted_data = sorted(data, key=lambda x: x.get("timestamp", ""), reverse=True)
    return sorted_data[:100]
