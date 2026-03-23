from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.models.document import Document
from backend.database.config import get_db
from pydantic import BaseModel
import os
import aiofiles
router = APIRouter()
UPLOAD_DIR = 'uploads/documents'
os.makedirs(UPLOAD_DIR, exist_ok=True)

class DocumentOut(BaseModel):
    id: int
    filename: str
    file_type: str
    category: str
    url: str

    class Config:
        orm_mode = True

@router.post('/documents/upload', response_model=DocumentOut)
async def upload_document(file: UploadFile=File(...), db: AsyncSession=Depends(get_db)):
    try:
        save_path = os.path.join(UPLOAD_DIR, file.filename)
        async with aiofiles.open(save_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        new_doc = Document(filename=file.filename, file_type=file.content_type, category='manual', url=save_path)
        db.add(new_doc)
        await db.commit()
        await db.refresh(new_doc)
        return new_doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete('/documents/{id}')
async def delete_document(id: int, db: AsyncSession=Depends(get_db)):
    result = await db.execute(select(Document).filter(Document.id == id))
    document = result.scalars().first()
    if not document:
        raise HTTPException(status_code=404, detail='Document not found')
    try:
        if os.path.exists(document.url):
            os.remove(document.url)
    except Exception:
        pass
    await db.delete(document)
    await db.commit()
    return {'status': 'deleted'}
