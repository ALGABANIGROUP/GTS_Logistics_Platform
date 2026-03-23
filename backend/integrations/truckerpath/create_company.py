import os
from typing import Optional
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
try:
    from backend.utils.role_protected import RoleChecker
    admin_required = RoleChecker(['admin'])
except Exception:
    admin_required = None
router = APIRouter(prefix='/integrations/truckerpath', tags=['TruckerPath'])
TRUCKERPATH_BASE_URL = os.getenv('TRUCKERPATH_BASE_URL', 'https://test-api.truckerpath.com/truckload/api').rstrip('/')
TRUCKERPATH_API_TOKEN = os.getenv('TRUCKERPATH_API_TOKEN', '')
TRUCKERPATH_ENABLE_MOCK = os.getenv('TRUCKERPATH_ENABLE_MOCK', 'true').lower() in {'1', 'true', 'yes'}

class CreateCompanyRequest(BaseModel):
    company_name: str = 'Gabani Transport Solutions LLC'
    company_dot: str = '4317957'
    company_mc: str = '1684192'
    company_email: EmailStr = 'freight@gabanilogistics.com'
    company_id: str = 'gabani_001'

class CreateCompanyResponse(BaseModel):
    ok: bool
    status: int
    provider: str = 'TruckerPath'
    data: Optional[dict] = None
    message: Optional[str] = None

def _headers() -> dict:
    token = TRUCKERPATH_API_TOKEN.strip()
    return {'Authorization': f'Bearer {token}' if token else '', 'Content-Type': 'application/json', 'Accept': 'application/json'}

@router.post('/company/create', response_model=CreateCompanyResponse, dependencies=[Depends(admin_required)] if admin_required else None)
async def create_company(body: CreateCompanyRequest) -> CreateCompanyResponse:
    """
    Create a company in TruckerPath via API.
    Uses TEST endpoint by default: https://test-api.truckerpath.com/truckload/api/company/create
    """
    if TRUCKERPATH_ENABLE_MOCK or not TRUCKERPATH_API_TOKEN:
        return CreateCompanyResponse(ok=True, status=200, data={'mock': True, 'echo': body.dict()}, message='Mock mode enabled or missing API token.')
    url = f'{TRUCKERPATH_BASE_URL}/company/create'
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, headers=_headers(), json=body.dict())
        status_code = resp.status_code
        if status_code in (200, 201):
            return CreateCompanyResponse(ok=True, status=status_code, data=resp.json())
        detail = None
        try:
            detail = resp.json()
        except Exception:
            detail = {'text': resp.text}
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail={'provider_status': status_code, 'provider_detail': detail})