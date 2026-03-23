from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from backend.database.session import get_async_session
from backend.models.platform_expense import PlatformExpense
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import json
import shutil
import re
import tempfile

router = APIRouter()


class PlatformExpenseCreate(BaseModel):
    title: str
    amount: float
    date: datetime
    notes: Optional[str] = None


class PlatformExpenseUpdate(BaseModel):
    title: Optional[str]
    amount: Optional[float]
    date: Optional[datetime]
    notes: Optional[str] = None


@router.get("/platform-expenses", response_model=List[PlatformExpenseCreate])
async def get_expenses(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(PlatformExpense))
    expenses = result.scalars().all()
    return expenses


@router.post("/platform-expenses", response_model=PlatformExpenseCreate)
async def create_expense(payload: PlatformExpenseCreate, session: AsyncSession = Depends(get_async_session)):
    new_expense = PlatformExpense(**payload.dict())
    session.add(new_expense)
    await session.commit()
    await session.refresh(new_expense)
    return new_expense


@router.put("/platform-expenses/{expense_id}")
async def update_expense(expense_id: int, payload: PlatformExpenseUpdate, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(PlatformExpense).where(PlatformExpense.id == expense_id))
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(expense, key, value)

    await session.commit()
    await session.refresh(expense)
    return expense


@router.delete("/platform-expenses/{expense_id}")
async def delete_expense(expense_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(PlatformExpense).where(PlatformExpense.id == expense_id))
    expense = result.scalar_one_or_none()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    await session.delete(expense)
    await session.commit()
    return {"deleted": expense_id}


@router.post("/expenses/{expense_id}/upload")
async def upload_expense_file(expense_id: str, file: UploadFile = File(...)):
    """Upload an attachment for an expense"""
    try:
        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "platform_reports", "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Sanitize filename
        filename = file.filename
        if not filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Prevent directory traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Create unique filename with expense_id prefix
        unique_filename = f"{expense_id}_{filename}"
        file_path = os.path.join(uploads_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "success": True,
            "filename": unique_filename,
            "size": os.path.getsize(file_path),
            "url": f"/api/v1/platform/expenses/{expense_id}/download"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


@router.get("/expenses/{expense_id}/download")
async def download_expense_file(expense_id: str):
    """Download an attachment for an expense"""
    try:
        uploads_dir = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "platform_reports", "uploads")
        
        # Find file with this expense_id prefix
        if not os.path.exists(uploads_dir):
            raise HTTPException(status_code=404, detail="File not found")
        
        files = [f for f in os.listdir(uploads_dir) if f.startswith(f"{expense_id}_")]
        if not files:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_path = os.path.join(uploads_dir, files[0])
        return FileResponse(path=file_path, filename=files[0].replace(f"{expense_id}_", ""))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")


@router.delete("/expenses/{expense_id}/delete-file")
async def delete_expense_file(expense_id: str):
    """Delete an attachment for an expense"""
    try:
        uploads_dir = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "platform_reports", "uploads")
        
        # Find file with this expense_id prefix
        if not os.path.exists(uploads_dir):
            raise HTTPException(status_code=404, detail="File not found")
        
        files = [f for f in os.listdir(uploads_dir) if f.startswith(f"{expense_id}_")]
        if not files:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_path = os.path.join(uploads_dir, files[0])
        os.remove(file_path)
        
        return {"success": True, "deleted": files[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")


@router.get("/expenses")
async def get_all_expenses():
    """Get all platform expenses from invoice_data.json"""
    try:
        # Read invoice data from JSON file
        invoice_data_path = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "platform_reports", "invoices", "invoice_data.json")
        
        if not os.path.exists(invoice_data_path):
            return []
        
        with open(invoice_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Transform invoice data into expense objects
        expenses = []
        category_map = {
            "AI": "api_services",
            "open Ai": "api_services",
            "Render": "hosting",
            "Quo": "sms_service"
        }
        
        for invoice in data.get("invoices", []):
            expenses.append({
                "id": f"{invoice['vendor']}|{invoice['filename'].replace('.pdf', '')}",
                "category": category_map.get(invoice['vendor'], "other"),
                "service_name": f"{invoice['vendor']} Invoice",
                "vendor": invoice['vendor'],
                "description": invoice.get('description', ''),
                "amount": invoice.get('amount', 0),
                "currency": invoice.get('currency', 'USD'),
                "billing_frequency": "one_time",
                "is_recurring": False,
                "invoice_number": invoice['filename'].replace('.pdf', ''),
                "invoice_url": f"/api/v1/platform/invoices/{invoice['vendor']}/{invoice['filename']}",
                "billing_date": invoice.get('date', '2026-02-01'),
                "due_date": None,
                "paid_date": invoice.get('date', '2026-02-01'),
                "is_paid": True,
                "is_active": False,
                "notes": f"Imported from docs - {invoice.get('description', '')}"
            })
        
        return expenses
    except Exception as e:
        print(f"Error reading invoice data: {e}")
        return []


@router.get("/expenses/summary")
async def get_expenses_summary():
    """Get platform expenses summary from invoice_data.json"""
    try:
        # Read invoice data from JSON file
        invoice_data_path = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "platform_reports", "invoices", "invoice_data.json")
        
        if not os.path.exists(invoice_data_path):
            return {
                "total": 0,
                "paid": 0,
                "pending": 0,
                "recurring_monthly": 0
            }
        
        with open(invoice_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Calculate summary from invoice data
        total = sum(float(inv.get('amount', 0)) for inv in data.get('invoices', []))
        paid = total  # All invoices are marked as paid
        pending = 0
        
        return {
            "total": round(total, 2),
            "paid": round(paid, 2),
            "pending": round(pending, 2),
            "recurring_monthly": 0  # All are one-time
        }
    except Exception as e:
        print(f"Error calculating summary: {e}")
        return {
            "total": 0,
            "paid": 0,
            "pending": 0,
            "recurring_monthly": 0
        }


@router.get("/platform-expenses/invoice/{vendor}/{filename}")
async def get_invoice_file(vendor: str, filename: str):
    """Serve invoice PDF files from docs/platform_reports/invoices/{vendor}/"""
    # Security: Validate vendor and filename to prevent directory traversal
    valid_vendors = ["AI", "Render", "Quo", "open Ai"]
    if vendor not in valid_vendors:
        raise HTTPException(status_code=400, detail="Invalid vendor")
    
    # Ensure filename ends with .pdf
    if not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Prevent directory traversal attacks
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Build file path
    base_path = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "platform_reports", "invoices", vendor)
    file_path = os.path.join(base_path, filename)
    
    # Verify file exists and is within the allowed directory
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Invoice file not found")
    
    # Ensure the resolved path is still within the intended directory (security check)
    real_path = os.path.realpath(file_path)
    real_base = os.path.realpath(base_path)
    if not real_path.startswith(real_base):
        raise HTTPException(status_code=400, detail="Invalid file request")
    
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=filename
    )


@router.get("/invoices/{vendor}/{filename}")
async def get_invoice_file_alt(vendor: str, filename: str):
    """Serve invoice PDF files from docs/platform_reports/invoices/{vendor}/ - Alternative route"""
    # Security: Validate vendor and filename to prevent directory traversal
    valid_vendors = ["AI", "Render", "Quo", "open Ai"]
    if vendor not in valid_vendors:
        raise HTTPException(status_code=400, detail="Invalid vendor")
    
    # Ensure filename ends with .pdf
    if not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Prevent directory traversal attacks
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Build file path
    base_path = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "platform_reports", "invoices", vendor)
    file_path = os.path.join(base_path, filename)
    
    # Verify file exists and is within the allowed directory
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Invoice file not found")
    
    # Ensure the resolved path is still within the intended directory (security check)
    real_path = os.path.realpath(file_path)
    real_base = os.path.realpath(base_path)
    if not real_path.startswith(real_base):
        raise HTTPException(status_code=400, detail="Invalid file request")
    
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=filename
    )

