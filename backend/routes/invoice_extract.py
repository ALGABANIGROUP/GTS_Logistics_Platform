from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.config import get_db_async
from backend.bots.invoice_ocr import extract_invoice_text
from backend.bots.invoice_ai_extract import extract_invoice_fields

router = APIRouter()

@router.post("/api/v1/invoice/extract-fields")
async def extract_invoice_fields_api(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_async),
):
    try:
        text = extract_invoice_text(file)
        fields = extract_invoice_fields(text)
        try:
            from backend.services.platform_webhook_dispatcher import dispatch_from_platform_settings

            await dispatch_from_platform_settings(
                db=db,
                event_type="invoice.extracted",
                data={
                    "invoice_number": fields.get("invoice_number"),
                    "vendor": fields.get("vendor"),
                    "amount": fields.get("amount"),
                    "currency": fields.get("currency"),
                    "due_date": fields.get("due_date"),
                },
            )
        except Exception:
            pass
        return {"fields": fields, "raw_text": text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
