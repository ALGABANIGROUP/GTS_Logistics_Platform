import asyncio
from backend.database.session import get_db
from backend.models.invoices import Invoice
from datetime import date

async def create_test_invoice():
    async for db in get_db():
        invoice = Invoice(
            number="INV-000001",
            date=date.today(),
            amount_usd=1250.00,
            status="pending",
            user_id=1
        )
        db.add(invoice)
        await db.commit()
        print(f"Created invoice with ID: {invoice.id}")
        break

if __name__ == "__main__":
    asyncio.run(create_test_invoice())