import io
from typing import List
from fastapi import UploadFile
from PIL import Image
import pytesseract

try:
    from pdf2image import convert_from_bytes
except Exception:  # pragma: no cover
    convert_from_bytes = None

SUPPORTED_IMAGE_TYPES = ["image/png", "image/jpeg", "image/jpg"]
SUPPORTED_DOC_TYPES = ["application/pdf"]

def is_image(file: UploadFile) -> bool:
    return file.content_type in SUPPORTED_IMAGE_TYPES

def is_pdf(file: UploadFile) -> bool:
    return file.content_type == "application/pdf"

def extract_text_from_image_bytes(image_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(image)
    return text

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    if convert_from_bytes is None:
        raise RuntimeError("PDF OCR requires pdf2image to be installed")
    images = convert_from_bytes(pdf_bytes)
    text = "\n".join([pytesseract.image_to_string(img) for img in images])
    return text

def extract_invoice_text(file: UploadFile) -> str:
    content = file.file.read()
    if is_image(file):
        return extract_text_from_image_bytes(content)
    elif is_pdf(file):
        return extract_text_from_pdf_bytes(content)
    else:
        raise ValueError("Unsupported file type: {}".format(file.content_type))

# Example usage in FastAPI endpoint:
# from fastapi import APIRouter, UploadFile, File
# router = APIRouter()
#
# @router.post("/extract-invoice-text")
# async def extract_invoice(file: UploadFile = File(...)):
#     text = extract_invoice_text(file)
#     return {"text": text}
