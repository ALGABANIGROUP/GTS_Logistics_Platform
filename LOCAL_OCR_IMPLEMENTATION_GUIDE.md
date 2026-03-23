# Free Local OCR Alternative Implementation Guide

## Setup EasyOCR (Local, Free, Offline)

```python
# In backend/routes/platform_infrastructure_routes.py

# Add to imports:
try:
    import easyocr
    EASYOCR_AVAILABLE = True
    # Initialize reader (takes time first time - loads models)
    ocr_reader = easyocr.Reader(['en'], gpu=False)
except ImportError:
    EASYOCR_AVAILABLE = False
    ocr_reader = None
```

## Local OCR Extraction Function

```python
async def _extract_from_image_local(content: bytes, file_ext: str) -> dict:
    """Extract invoice data using FREE local OCR (EasyOCR)"""
    if not EASYOCR_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Local OCR not available. Install: pip install easyocr"
        )
    
    import io
    from PIL import Image
    import re
    
    # Load image
    image = Image.open(io.BytesIO(content))
    
    # Extract text with EasyOCR
    result = ocr_reader.readtext(image, detail=0)
    full_text = ' '.join(result)
    
    # Parse with regex patterns
    extracted = {}
    
    # Amount (e.g., $125.50, 125.50, $125)
    amount_match = re.search(r'\$?\s*(\d+[,\.]?\d*\.?\d+)', full_text)
    if amount_match:
        extracted['amount'] = float(amount_match.group(1).replace(',', ''))
    
    # Date (e.g., 01/15/2026, 2026-01-15)
    date_match = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', full_text)
    if date_match:
        date_str = date_match.group(1)
        # Convert to YYYY-MM-DD
        try:
            from dateutil import parser
            extracted['billing_date'] = parser.parse(date_str).strftime('%Y-%m-%d')
        except:
            extracted['billing_date'] = None
    
    # Invoice number
    inv_match = re.search(r'(?:INV|Invoice|Receipt)[#:\s-]*(\w+)', full_text, re.I)
    if inv_match:
        extracted['invoice_number'] = inv_match.group(1)
    
    # Vendor/Company name (usually first line or has "Inc", "LLC")
    vendor_match = re.search(r'^([A-Z][A-Za-z\s&]+(?:Inc|LLC|Ltd|Corp)?)', full_text)
    if vendor_match:
        extracted['vendor'] = vendor_match.group(1).strip()
    
    # Currency
    if '$' in full_text:
        extracted['currency'] = 'USD'
    elif '€' in full_text:
        extracted['currency'] = 'EUR'
    else:
        extracted['currency'] = 'USD'
    
    # Service name (keywords)
    keywords = {
        'hosting': ['hosting', 'cloud', 'server', 'vps'],
        'domain': ['domain', 'dns', 'godaddy', 'namecheap'],
        'database': ['database', 'postgres', 'mysql', 'mongodb'],
        'phone': ['phone', 'mobile', 'cellular', 'twilio'],
    }
    
    text_lower = full_text.lower()
    for category, words in keywords.items():
        if any(word in text_lower for word in words):
            extracted['category'] = category
            break
    
    # Description (first 100 chars of text)
    extracted['description'] = full_text[:100].strip()
    
    return extracted
```

## Update Extraction Endpoint

```python
@router.post("/expenses/extract-invoice", response_model=dict)
async def extract_invoice_data(
    files: List[UploadFile] = File(...),
    use_local_ocr: bool = Query(False, description="Use free local OCR instead of OpenAI")
):
    """
    Upload invoice files (up to 30) and extract data.
    - use_local_ocr=True: FREE local OCR (EasyOCR)
    - use_local_ocr=False: OpenAI API (paid, more accurate)
    """
    if not use_local_ocr and not OPENAI_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="OpenAI not available. Try use_local_ocr=true for free extraction"
        )
    
    if len(files) > 30:
        raise HTTPException(
            status_code=400,
            detail="Maximum 30 files allowed"
        )
    
    results = []
    
    for file in files:
        try:
            file_ext = os.path.splitext(file.filename or "")[1].lower()
            content = await file.read()
            
            extracted_data = None
            
            # Image files
            if file_ext in {".png", ".jpg", ".jpeg"}:
                if use_local_ocr:
                    # FREE local OCR
                    extracted_data = await _extract_from_image_local(content, file_ext)
                else:
                    # OpenAI Vision API (paid)
                    import base64
                    base64_image = base64.b64encode(content).decode('utf-8')
                    extracted_data = await _extract_from_vision_api(file_ext, base64_image)
            
            # PDF files
            elif file_ext == ".pdf":
                try:
                    import PyPDF2
                    import io
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    
                    if use_local_ocr:
                        # Parse with regex (free)
                        extracted_data = await _extract_from_text_local(text)
                    else:
                        # Parse with OpenAI (paid)
                        extracted_data = await _extract_from_text(text)
                except ImportError:
                    results.append({
                        "filename": file.filename,
                        "success": False,
                        "error": "PDF support requires PyPDF2"
                    })
                    continue
            
            if extracted_data:
                results.append({
                    "filename": file.filename,
                    "success": True,
                    "extracted_data": extracted_data,
                    "extraction_method": "local_ocr" if use_local_ocr else "openai"
                })
        
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
    
    successful = sum(1 for r in results if r.get("success"))
    
    return {
        "success": successful > 0,
        "total_files": len(files),
        "successful_extractions": successful,
        "failed_extractions": len(files) - successful,
        "results": results,
        "message": f"Processed {len(files)} files using {'local OCR (free)' if use_local_ocr else 'OpenAI API (paid)'}"
    }
```

## Frontend Integration

```javascript
// In PlatformExpenses.jsx
const handleAIExtract = async (files, useLocalOCR = false) => {
    const formData = new FormData();
    for (let file of files) {
        formData.append("files", file);
    }
    
    // Add query parameter for local OCR
    const endpoint = useLocalOCR 
        ? "/api/v1/platform/expenses/extract-invoice?use_local_ocr=true"
        : "/api/v1/platform/expenses/extract-invoice";
    
    const response = await axiosClient.post(endpoint, formData, {
        headers: { "Content-Type": "multipart/form-data" }
    });
    
    // ... handle response
};
```

## UI Update

```jsx
{/* In modal */}
<div className="flex gap-2">
    <label className="flex-1 btn btn-primary">
        <input type="file" multiple onChange={(e) => handleAIExtract(e.target.files, false)} />
        🤖 OpenAI Extract (Paid, Accurate)
    </label>
    
    <label className="flex-1 btn btn-success">
        <input type="file" multiple onChange={(e) => handleAIExtract(e.target.files, true)} />
        🆓 Local OCR (Free, Good)
    </label>
</div>
```

---

## Comparison Table

| Feature | EasyOCR (Local) | OpenAI API |
|---------|-----------------|------------|
| **Cost** | 🆓 FREE | 💰 $0.01/image |
| **Accuracy** | 85-90% | 95-98% |
| **Speed** | 2-5 sec/image | 3-5 sec/image |
| **Offline** | ✅ Yes | ❌ No |
| **Setup** | `pip install easyocr` | API key needed |
| **Languages** | 80+ | All |
| **Privacy** | 🔒 100% local | ⚠️ Sent to OpenAI |

---

## Quick Start

```bash
# Install
pip install easyocr

# Test
python -c "import easyocr; reader = easyocr.Reader(['en']); print('EasyOCR ready!')"
```

---

## Notes

- EasyOCR loads models (~400MB) first time - takes time
- Prefer GPU if available (10x faster)
- For Arabic invoices: `easyocr.Reader(['ar', 'en'])`
- Tesseract is lighter (50MB) but less accurate

---

## Recommendation

**For production**: Use both together:
1. **EasyOCR first** (free) for simple invoices
2. **OpenAI as fallback** (paid) for complex invoices or OCR failure

This saves 80-90% of costs! 💰
