from fastapi import APIRouter, UploadFile, File, HTTPException

import easyocr
import tempfile
import os
from typing import Dict
from pdf2image import convert_from_path

router = APIRouter()

reader = easyocr.Reader(['en'], gpu=False)

def extract_invoice_fields(text: str) -> Dict:
    # Very basic extraction logic (improve as needed)
    import re
    fields = {}
    # Invoice number
    match = re.search(r"Invoice number[:\s]*([\w\-]+)", text, re.I)
    if match:
        fields['invoice_number'] = match.group(1)
    # Date of issue
    match = re.search(r"Date of issue[:\s]*([\w\s,]+)", text, re.I)
    if match:
        fields['issue_date'] = match.group(1).strip()
    # Amount (USD)
    match = re.search(r"\$([0-9,.]+)", text)
    if match:
        fields['amount'] = match.group(1)
    # Vendor (first line or Render)
    match = re.search(r"^([A-Za-z0-9 .,&'-]+)\n", text)
    if match:
        fields['vendor'] = match.group(1).strip()
    return fields


@router.post("/ocr-invoice-extract")
async def ocr_invoice_extract(file: UploadFile = File(...)):
    filename = file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="Uploaded file must include a filename.")
    filename = str(filename)

    try:
        suffix = os.path.splitext(filename)[1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        text = ""
        if suffix in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            result = reader.readtext(tmp_path, detail=0, paragraph=True)
            text = "\n".join(result)
        elif suffix == '.pdf':
            # Convert PDF pages to images
            images = convert_from_path(tmp_path)
            all_text = []
            for img in images:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as img_tmp:
                    img.save(img_tmp.name, format='PNG')
                    ocr_result = reader.readtext(img_tmp.name, detail=0, paragraph=True)
                    all_text.append("\n".join(ocr_result))
                    os.unlink(img_tmp.name)
            text = "\n".join(all_text)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type for OCR.")
        fields = extract_invoice_fields(text)
        os.unlink(tmp_path)
        return {"success": True, "fields": fields, "raw_text": text}
    except Exception as e:
        return {"success": False, "error": str(e)}
