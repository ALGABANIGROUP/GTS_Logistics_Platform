from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

router = APIRouter()

class Email(BaseModel):
    subject: str
    timestamp: str
    from_: str
    body: str
    reply: str | None = None

emails_db: List[Email] = [
    Email(
        subject="Request for Quote",
        timestamp="2025-05-02 11:24",
        from_="john@example.com",
        body="Can you send me a quote?",
        reply="Thanks for your request! Our team will contact you shortly."
    ),
    Email(
        subject="Invoice Issue",
        timestamp="2025-05-01 15:12",
        from_="billing@client.com",
        body="The invoice INV-2025-123 seems wrong.",
        reply="We've received your request and will review the invoice."
    ),
]

@router.get("/api/emails", response_model=List[Email])
async def get_emails():
    return emails_db
