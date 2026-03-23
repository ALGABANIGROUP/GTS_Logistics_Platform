from fastapi import APIRouter
from fastapi.responses import FileResponse
from openpyxl import Workbook
from datetime import datetime
import os
import threading

router = APIRouter()

@router.get("/export-shipments")
def export_shipments():
    wb = Workbook()
    ws = wb.active
    if ws is None:
        raise Exception("❌ Failed to create Excel worksheet")

    ws.title = "Shipments"
    ws.append(["ID", "Pickup", "Dropoff", "Trailer Type", "Rate ($)", "Weight"])

    shipments = [
        [1, "Seattle", "Denver", "Flatbed", 2300, "42,000 lbs"],
        [2, "Dallas", "Phoenix", "Reefer", 1800, "39,000 lbs"],
        [3, "Miami", "Atlanta", "Dry Van", 2100, "40,500 lbs"],
    ]

    for row in shipments:
        ws.append(row)

    filename = f"shipments_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    wb.save(filename)

    def delayed_cleanup(file_path):
        import time
        time.sleep(2)
        if os.path.exists(file_path):
            os.remove(file_path)

    threading.Thread(target=delayed_cleanup, args=(filename,), daemon=True).start()

    return FileResponse(
        path=filename,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
