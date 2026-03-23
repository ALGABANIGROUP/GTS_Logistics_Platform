import re
from typing import Dict

def extract_invoice_fields(text: str) -> Dict[str, str]:
    """
    Extract common invoice fields from unstructured text.
    """
    fields = {}
    # Invoice number
    invoice_no = re.search(r"Invoice\s*#?:?\s*([\w-]+)", text, re.IGNORECASE)
    if invoice_no:
        fields["invoice_number"] = invoice_no.group(1)
    # Total amount
    amount = re.search(r"Total\s*:?\s*\$?([\d,]+\.\d{2})", text, re.IGNORECASE)
    if amount:
        fields["amount"] = amount.group(1)
    # Invoice date
    date = re.search(r"(\d{2,4}[/-]\d{1,2}[/-]\d{1,4})", text)
    if date:
        fields["date"] = date.group(1)
    # Vendor name
    vendor = re.search(r"Vendor\s*:?\s*([\w .,&-]+)", text, re.IGNORECASE)
    if vendor:
        fields["vendor"] = vendor.group(1)
    return fields

# Example:
# fields = extract_invoice_fields(text)
# print(fields)
