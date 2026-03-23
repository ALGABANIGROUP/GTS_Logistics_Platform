from fastapi import APIRouter
import os

router = APIRouter(prefix="/finance", tags=["Platform Expenses"])

@router.get("/expenses")
def get_platform_expenses():
    # Scan docs/platform_reports/invoices for PDF files
    invoices_dir = os.path.join(os.path.dirname(__file__), '../../docs/platform_reports/invoices')
    try:
        files = [f for f in os.listdir(invoices_dir) if f.endswith('.pdf')]
        items = [{"filename": f, "url": f"/static/platform_reports/invoices/{f}"} for f in files]
        return {"items": items, "count": len(items)}
    except Exception as e:
        return {"items": [], "count": 0, "error": str(e)}
