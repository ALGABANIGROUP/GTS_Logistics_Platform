from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.bots.invoice_ocr import extract_invoice_text

router = APIRouter()

@router.post("/api/v1/invoice/extract-text")
async def extract_invoice_text_api(file: UploadFile = File(...)):
    try:
        text = extract_invoice_text(file)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
