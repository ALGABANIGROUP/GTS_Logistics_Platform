import os
import aiofiles
import pytesseract
from pdf2image import convert_from_bytes
from datetime import datetime
import re

UPLOAD_DIR = "uploads/documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Save file to disk and extract text using OCR (PDF/Image only)
async def save_file_and_extract_text(file):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    # Extract text based on file type
    if file.filename.lower().endswith(".pdf"):
        images = convert_from_bytes(content)
        text = "\n".join([pytesseract.image_to_string(img) for img in images])
    elif file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        with open(file_path, 'rb') as img_file:
            text = pytesseract.image_to_string(img_file.read())
    else:
        text = "[Unsupported file type for OCR]"

    return file_path, text

# Extract expiry date from scanned text using regex
def extract_expiry_date(text):
    date_patterns = [
        r"\b(\d{2}/\d{2}/\d{4})\b",  # 12/03/2025
        r"\b(\d{4}-\d{2}-\d{2})\b",  # 2025-03-12
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return datetime.strptime(match.group(1), "%d/%m/%Y")
            except:
                try:
                    return datetime.strptime(match.group(1), "%Y-%m-%d")
                except:
                    continue
    return None
