"""Invoice extraction endpoint using OCR and text pattern matching"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from datetime import datetime
import os
import re
import tempfile

router = APIRouter()


def extract_text_from_file(file_path: str, filename: str) -> str:
    """Extract text from PDF or image files"""
    text = ""
    
    try:
        # Handle PDF files
        if filename.lower().endswith('.pdf'):
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""
            except ImportError:
                # Fallback if pdfplumber not installed
                text = "PDF extraction requires: pip install pdfplumber"
        
        # Handle image files (PNG, JPG, etc.)
        elif filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            try:
                import pytesseract
                from PIL import Image
                image = Image.open(file_path)
                text = pytesseract.image_to_string(image)
            except ImportError:
                text = "Image OCR requires: pip install pytesseract pillow"
            except Exception as e:
                text = f"OCR Error: {str(e)}"
        
        # Handle text files
        elif filename.lower().endswith(('.txt', '.csv')):
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        else:
            text = "Unsupported file type"
    
    except Exception as e:
        text = f"Error reading file: {str(e)}"
    
    return text


def extract_invoice_data(text: str, filename: str) -> dict:
    """Extract structured invoice data from text using regex"""
    normalized_text = " ".join(text.split())
    
    # Regular expressions for common patterns
    amount_pattern = r'(?:Total|Amount|Price|Cost|Due|Invoice Total|USD|Subtotal|Net)[\s:]*\$?([0-9,]+[\.,][0-9]{2})'
    invoice_number_pattern = r'(?:Invoice\s*number|Invoice\s*#|Invoice\s*No|Invoice|Inv|Reference|Order|PO|Bill|#)\s*[:#]?\s*([A-Z0-9\-\_\.]+)'
    transaction_id_pattern = r'(?:Transaction\s*ID|Transaction\s*Id)[\s:]*([A-Z0-9\-\_]+)'
    date_pattern = r'(\d{1,2}[\/-]\d{1,2}[\/-]\d{2,4}|\w+\s+\d{1,2}(?:,)?\s+\d{4}|\d{4}[\/-]\d{1,2}[\/-]\d{1,2})'
    vendor_pattern = r'(?:From|Vendor|Provider|Company|Bill From|Billed By)[\s:]*([A-Za-z0-9\s&.]+?)(?:\n|$|Contact|Phone)'
    
    # Extract amounts
    amounts = re.findall(amount_pattern, normalized_text, re.IGNORECASE)
    amount = 0.0
    if amounts:
        # Take the first amount found and normalize separators
        amount_str = amounts[0].strip()
        if "," in amount_str and "." in amount_str:
            # Assume comma is thousands separator
            amount_str = amount_str.replace(",", "")
        elif "," in amount_str and "." not in amount_str:
            # Assume comma is decimal separator
            amount_str = amount_str.replace(",", ".")
        try:
            amount = float(amount_str)
        except ValueError:
            pass
    
    # Extract invoice number (or transaction id for receipts)
    invoice_number = ""
    invoice_match = re.search(invoice_number_pattern, normalized_text, re.IGNORECASE)
    if invoice_match:
        invoice_number = invoice_match.group(1).strip()
    else:
        txn_match = re.search(transaction_id_pattern, normalized_text, re.IGNORECASE)
        if txn_match:
            invoice_number = txn_match.group(1).strip()
        else:
            alt_invoice_match = re.search(r"\b[A-Z0-9]{4,}-\d{4}\b", normalized_text)
            if alt_invoice_match:
                invoice_number = alt_invoice_match.group(0)
            else:
            # Fallback: use filename without extension
                invoice_number = filename.rsplit('.', 1)[0]

    if invoice_number.lower() in {"invoice", "inv", "receipt"}:
        invoice_number = filename.rsplit('.', 1)[0]
    
    # Extract date
    billing_date = datetime.now().strftime('%Y-%m-%d')
    due_date = None
    issue_match = re.search(
        rf"(?:Date\s*of\s*issue|Invoice\s*Date|Issue\s*Date|Issued|Bill\s*Date)\s*[:]*\s*{date_pattern}",
        normalized_text,
        re.IGNORECASE,
    )
    if issue_match:
        parsed_issue = parse_date_string(issue_match.group(1))
        if parsed_issue:
            billing_date = parsed_issue

    due_match = re.search(
        rf"(?:Date\s*due|Due\s*date|Amount\s+due|due)\s*[:]*\s*{date_pattern}",
        normalized_text,
        re.IGNORECASE,
    )
    if due_match:
        parsed_due = parse_date_string(due_match.group(1))
        if parsed_due:
            due_date = parsed_due
    
    # Extract vendor/company name
    vendor = detect_vendor(text)
    if vendor == "Unknown Vendor":
        vendor_match = re.search(vendor_pattern, text, re.IGNORECASE)
        if vendor_match:
            vendor_name = vendor_match.group(1).strip()
            if vendor_name and len(vendor_name) > 2:
                vendor = vendor_name
    
    # Detect currency
    currency = "USD"
    if re.search(r'€|EUR', text, re.IGNORECASE):
        currency = "EUR"
    elif re.search(r'£|GBP', text, re.IGNORECASE):
        currency = "GBP"
    elif re.search(r'¥|JPY', text, re.IGNORECASE):
        currency = "JPY"
    elif re.search(r'₹|INR', text, re.IGNORECASE):
        currency = "INR"
    
    category = infer_category(text, vendor)
    billing_frequency = infer_billing_frequency(text)

    service_name = extract_service_name(text, vendor)

    return {
        "service_name": service_name,
        "vendor": vendor,
        "amount": round(amount, 2),
        "currency": currency,
        "invoice_number": invoice_number,
        "billing_date": billing_date,
        "due_date": due_date,
        "description": f"Extracted from {filename}",
        "category": category,
        "billing_frequency": billing_frequency,
        "is_recurring": billing_frequency in {"monthly", "quarterly", "yearly"}
    }


def infer_category(text: str, vendor: str) -> str:
    """Infer expense category from invoice text and vendor name."""
    haystack = f"{vendor}\n{text}".lower()

    keyword_map = [
        ("database", ["database", "postgres", "postgresql", "mysql", "mongodb", "db", "rds", "sql"]),
        ("hosting", ["hosting", "server", "compute", "render", "digitalocean", "linode", "heroku", "aws", "ec2"]),
        ("domain", ["domain", "dns", "registrar", "nameserver"]),
        ("phone", ["phone", "telecom", "voip", "call minutes", "mobile"]),
        ("virtual_office", ["virtual office", "cowork", "office suite"]),
        ("api_services", ["api", "openai", "anthropic", "gpt", "llm", "api usage"]),
        ("cloud_storage", ["storage", "s3", "bucket", "object storage", "blob storage"]),
        ("email_service", ["email", "smtp", "mailgun", "sendgrid", "postmark"]),
        ("sms_service", ["sms", "message", "twilio", "sms service"]),
        ("payment_gateway", ["payment", "gateway", "stripe", "paypal", "checkout", "merchant"]),
        ("monitoring", ["monitoring", "uptime", "statuspage", "observability", "datadog"]),
        ("security", ["security", "waf", "firewall", "ssl", "vpn"]),
        ("backup", ["backup", "snapshot", "recovery"]),
        ("cdn", ["cdn", "cloudflare", "edge cache"]),
    ]

    for category, keywords in keyword_map:
        if any(keyword in haystack for keyword in keywords):
            return category

    return "other"


def infer_billing_frequency(text: str) -> str:
    """Infer billing frequency from a date range in the invoice text."""
    normalized_text = " ".join(text.split())
    range_match = re.search(
        r"([A-Za-z]{3,9}\s+\d{1,2}(?:,?\s*\d{4})?)\s*(?:-|–|to)\s*([A-Za-z]{3,9}\s+\d{1,2}(?:,?\s*\d{4})?)",
        normalized_text,
        re.IGNORECASE,
    )
    if not range_match:
        return "one_time"

    start_raw = range_match.group(1)
    end_raw = range_match.group(2)

    end_date = parse_named_date(end_raw)
    start_date = parse_named_date(start_raw, fallback_year=end_date.year if end_date else None)

    if not start_date or not end_date:
        return "one_time"

    delta_days = (end_date - start_date).days
    if 27 <= delta_days <= 32:
        return "monthly"
    if 85 <= delta_days <= 95:
        return "quarterly"
    if 360 <= delta_days <= 370:
        return "yearly"
    return "one_time"


def parse_named_date(value: str, fallback_year: int | None = None) -> datetime | None:
    """Parse dates like 'Feb 6, 2026' or 'Feb 6 2026'."""
    match = re.search(r"([A-Za-z]{3,9})\s+(\d{1,2})(?:,?\s*(\d{4}))?", value)
    if not match:
        return None

    month_name = match.group(1).lower()
    day = int(match.group(2))
    year_str = match.group(3)

    month_map = {
        "jan": 1,
        "january": 1,
        "feb": 2,
        "february": 2,
        "mar": 3,
        "march": 3,
        "apr": 4,
        "april": 4,
        "may": 5,
        "jun": 6,
        "june": 6,
        "jul": 7,
        "july": 7,
        "aug": 8,
        "august": 8,
        "sep": 9,
        "sept": 9,
        "september": 9,
        "oct": 10,
        "october": 10,
        "nov": 11,
        "november": 11,
        "dec": 12,
        "december": 12,
    }

    month = month_map.get(month_name)
    if not month:
        return None

    year = int(year_str) if year_str else fallback_year
    if not year:
        return None

    try:
        return datetime(year, month, day)
    except ValueError:
        return None


def parse_date_string(value: str) -> str | None:
    """Parse common date formats and return ISO (YYYY-MM-DD)."""
    value = value.strip()
    for fmt in ("%m/%d/%Y", "%m-%d-%Y", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue

    named = parse_named_date(value)
    if named:
        return named.date().isoformat()

    return None


def detect_vendor(text: str) -> str:
    """Detect known vendors from invoice text."""
    haystack = text.lower()
    vendor_map = [
        ("Render", ["render"]),
        ("OpenAI", ["openai"]),
        ("GitHub", ["github"]),
        ("Quo", ["quo", "openphone"]),
    ]
    for name, keywords in vendor_map:
        if any(keyword in haystack for keyword in keywords):
            return name
    return "Unknown Vendor"


def extract_service_name(text: str, vendor: str) -> str:
    """Pick a service name from the description line if possible."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for idx, line in enumerate(lines):
        if line.lower() == "description" and idx + 1 < len(lines):
            candidate = lines[idx + 1]
            # Skip header-like lines
            if candidate.lower().startswith("amount") or candidate.lower().startswith("subtotal"):
                continue
            return candidate

    return vendor


@router.post("/extract-invoice")
async def extract_invoice(files: List[UploadFile] = File(...)):
    """
    Extract invoice data from uploaded files (PDF, PNG, JPG, etc.)
    Returns extracted data for auto-filling the form
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 30:
        raise HTTPException(status_code=400, detail="Maximum 30 files allowed")
    
    results = []
    
    for file in files:
        try:
            filename = file.filename or "unknown.pdf"
            
            # Save file temporarily
            suffix = os.path.splitext(filename)[1] or ".bin"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp_path = tmp.name
                content = await file.read()
                tmp.write(content)
            
            # Extract text
            text = extract_text_from_file(tmp_path, filename)
            
            # Extract structured data
            if text and not any(err in text for err in ["requires:", "Unsupported file type"]):
                extracted_data = extract_invoice_data(text, filename)
                results.append({
                    "success": True,
                    "filename": filename,
                    "extracted_data": extracted_data
                })
            else:
                results.append({
                    "success": False,
                    "filename": filename,
                    "error": text if text else "Could not extract text from file"
                })
            
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except:
                pass
        
        except Exception as e:
            results.append({
                "success": False,
                "filename": file.filename or "unknown",
                "error": f"Processing error: {str(e)}"
            })
    
    return {
        "success": len([r for r in results if r.get("success")]) > 0,
        "results": results
    }
