import os
import hmac
import json
import hashlib
from typing import Optional, List, Dict, Any, Literal
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field, HttpUrl
try:
    from backend.utils.role_protected import RoleChecker
    admin_required = RoleChecker(['admin'])
except Exception:
    admin_required = None
router = APIRouter(prefix='/integrations/truckerpath', tags=['TruckerPath'])
TP_BASE_URL = os.getenv('TRUCKERPATH_BASE_URL', 'https://test-api.truckerpath.com/truckload/api').rstrip('/')
TP_TOKEN = os.getenv('TRUCKERPATH_API_TOKEN', '').strip()
TP_ENABLE_MOCK = os.getenv('TRUCKERPATH_ENABLE_MOCK', 'true').lower() in {'1', 'true', 'yes'}
TP_WEBHOOK_SECRET = os.getenv('TRUCKERPATH_WEBHOOK_SECRET', '').strip()
TP_POST_LOAD_URL = os.getenv('TRUCKERPATH_POST_LOAD_URL', f'{TP_BASE_URL}/shipments/v2')
TP_CREATE_COMPANY_URL = os.getenv('TRUCKERPATH_CREATE_COMPANY_URL', f'{TP_BASE_URL}/company/create')
TP_REGISTER_WEBHOOK_URL = os.getenv('TRUCKERPATH_REGISTER_WEBHOOK_URL', f'{TP_BASE_URL}/webhooks/register')
TP_REGISTER_WEBHOOK_ADD_URL = os.getenv('TRUCKERPATH_REGISTER_WEBHOOK_ADD_URL', f'{TP_BASE_URL}/webhooks/add')
TP_TRACKING_CREATE_URL = os.getenv('TRUCKERPATH_TRACKING_CREATE_URL', f'{TP_BASE_URL}/tracking/').rstrip('/') + '/'
TP_TRACKING_POINTS_URL = os.getenv('TRUCKERPATH_TRACKING_URL', f'{TP_BASE_URL}/tracking/update')

def _headers() -> Dict[str, str]:
    return {'Authorization': TP_TOKEN if TP_TOKEN else '', 'Content-Type': 'application/json', 'Accept': 'application/json'}

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

class Stop(BaseModel):
    type: Literal['PICKUP', 'DROPOFF']
    state: str
    city: str
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    date_local: Optional[str] = None

class ShipmentInfo(BaseModel):
    equipment: List[str]
    load_size: Literal['FULL', 'PARTIAL']
    description: Optional[str] = None
    shipment_weight: Optional[int] = None
    shipment_dimensions: Optional[dict] = Field(default_factory=dict)
    requirements: Optional[str] = None
    stop_list: List[Stop]

class ContactInfo(BaseModel):
    contact_email: EmailStr
    contact_first_name: str
    contact_last_name: str
    contact_phone_number: str
    contact_phone_ext: Optional[str] = ''

class PostLoadRequest(BaseModel):
    company_id: str
    contact_info: ContactInfo
    shipment_info: ShipmentInfo

class PostLoadResponse(BaseModel):
    ok: bool
    status: int
    provider: str = 'TruckerPath'
    data: Optional[dict] = None
    message: Optional[str] = None

class RegisterWebhookRequest(BaseModel):
    url: HttpUrl
    events: List[str] = Field(default_factory=lambda : ['tracking.update', 'load.status', 'load.booked'])

class RegisterWebhookResponse(BaseModel):
    ok: bool
    status: int
    provider: str = 'TruckerPath'
    webhook_id: Optional[str] = None
    data: Optional[dict] = None
    message: Optional[str] = None

class RegisterWebhookAddRequest(BaseModel):
    url: HttpUrl
    type: Literal['BOOK', 'BID'] = 'BOOK'

class RegisterWebhookAddResponse(BaseModel):
    ok: bool
    status: int
    provider: str = 'TruckerPath'
    data: Optional[dict] = None
    message: Optional[str] = None

class LocationBlock(BaseModel):
    state: str
    city: str
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    date_local: Optional[str] = None

class TrackingCreateRequest(BaseModel):
    carrier_name: str
    carrier_phone: str
    carrier_email: EmailStr
    pick_up: LocationBlock
    drop_off: LocationBlock
    note: Optional[str] = None
    shipper_notify_email: Optional[EmailStr] = None
    is_arrival_notified: Optional[bool] = True

class GenericProviderResponse(BaseModel):
    ok: bool
    status: int
    provider: str = 'TruckerPath'
    data: Optional[dict] = None
    message: Optional[str] = None

class TrackingPoint(BaseModel):
    shipment_id: Optional[str] = None
    load_id: Optional[str] = None
    lat: float
    lng: float
    speed: Optional[float] = None
    heading: Optional[float] = None
    ts: str

class TrackingPointsRequest(BaseModel):
    company_id: Optional[str] = None
    device_id: Optional[str] = None
    points: List[TrackingPoint]

def _raise_provider_error(resp: httpx.Response) -> None:
    try:
        detail = resp.json()
    except Exception:
        detail = {'text': resp.text}
    raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail={'provider_status': resp.status_code, 'provider_detail': detail})

def _verify_signature(raw_body: bytes, provided_signature: Optional[str]) -> bool:
    if not TP_WEBHOOK_SECRET:
        return True
    if not provided_signature:
        return False
    provided = provided_signature.split('=', 1)[-1].strip()
    mac = hmac.new(TP_WEBHOOK_SECRET.encode('utf-8'), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, provided)

@router.get('/ping', response_model=GenericProviderResponse)
async def tp_ping() -> GenericProviderResponse:
    if TP_ENABLE_MOCK or not TP_TOKEN:
        return GenericProviderResponse(ok=True, status=200, data={'mock': True, 'message': 'Ping OK (mock)'})
    return GenericProviderResponse(ok=True, status=200, data={'message': 'Ping OK (no provider ping)'})

@router.post('/company/create', response_model=CreateCompanyResponse, dependencies=[Depends(admin_required)] if admin_required else None)
async def create_company(body: CreateCompanyRequest) -> CreateCompanyResponse:
    if TP_ENABLE_MOCK or not TP_TOKEN:
        return CreateCompanyResponse(ok=True, status=200, data={'mock': True, 'echo': body.dict()}, message='Mock mode or missing token')
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(TP_CREATE_COMPANY_URL, headers=_headers(), json=body.dict())
        if resp.status_code in (200, 201):
            return CreateCompanyResponse(ok=True, status=resp.status_code, data=resp.json())
        _raise_provider_error(resp)

@router.post('/post-load', response_model=PostLoadResponse, dependencies=[Depends(admin_required)] if admin_required else None)
async def post_load(body: PostLoadRequest) -> PostLoadResponse:
    if TP_ENABLE_MOCK or not TP_TOKEN:
        return PostLoadResponse(ok=True, status=200, data={'mock': True, 'echo': body.dict()}, message='Mock mode or missing token')
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(TP_POST_LOAD_URL, headers=_headers(), json=body.dict())
        if resp.status_code in (200, 201):
            return PostLoadResponse(ok=True, status=resp.status_code, data=resp.json())
        _raise_provider_error(resp)

@router.post('/register-webhook', response_model=RegisterWebhookResponse, dependencies=[Depends(admin_required)] if admin_required else None)
async def register_webhook(body: RegisterWebhookRequest) -> RegisterWebhookResponse:
    if TP_ENABLE_MOCK or not TP_TOKEN:
        return RegisterWebhookResponse(ok=True, status=200, webhook_id='mock-webhook-id', data={'mock': True, 'echo': body.dict()}, message='Mock mode or missing token')
    payload = {'url': str(body.url), 'events': body.events}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(TP_REGISTER_WEBHOOK_URL, headers=_headers(), json=payload)
        if resp.status_code in (200, 201):
            data = resp.json()
            webhook_id = str(data.get('id') or data.get('webhook_id') or '')
            return RegisterWebhookResponse(ok=True, status=resp.status_code, webhook_id=webhook_id, data=data)
        _raise_provider_error(resp)

@router.post('/register-webhook/add', response_model=RegisterWebhookAddResponse, dependencies=[Depends(admin_required)] if admin_required else None)
async def register_webhook_add(body: RegisterWebhookAddRequest) -> RegisterWebhookAddResponse:
    if TP_ENABLE_MOCK or not TP_TOKEN:
        return RegisterWebhookAddResponse(ok=True, status=200, data={'mock': True, 'echo': body.dict()}, message='Mock mode or missing token')
    payload = {'url': str(body.url), 'type': body.type}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(TP_REGISTER_WEBHOOK_ADD_URL, headers=_headers(), json=payload)
        if resp.status_code in (200, 201):
            return RegisterWebhookAddResponse(ok=True, status=resp.status_code, data=resp.json())
        _raise_provider_error(resp)

@router.post('/tracking/create', response_model=GenericProviderResponse)
async def tracking_create(body: TrackingCreateRequest) -> GenericProviderResponse:
    if TP_ENABLE_MOCK or not TP_TOKEN:
        return GenericProviderResponse(ok=True, status=200, data={'mock': True, 'echo': body.dict()}, message='Mock mode or missing token')
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(TP_TRACKING_CREATE_URL, headers=_headers(), json=body.dict())
        if resp.status_code in (200, 201):
            return GenericProviderResponse(ok=True, status=resp.status_code, data=resp.json())
        _raise_provider_error(resp)

@router.post('/tracking', response_model=GenericProviderResponse)
async def push_tracking(body: TrackingPointsRequest) -> GenericProviderResponse:
    if TP_ENABLE_MOCK or not TP_TOKEN:
        return GenericProviderResponse(ok=True, status=200, data={'mock': True, 'echo': body.dict()}, message='Mock mode or missing token')
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(TP_TRACKING_POINTS_URL, headers=_headers(), json=body.dict())
        if resp.status_code in (200, 201, 202):
            return GenericProviderResponse(ok=True, status=resp.status_code, data=resp.json())
        _raise_provider_error(resp)

@router.post('/webhook')
async def webhook_receiver(request: Request):
    raw = await request.body()
    sig = request.headers.get('X-TruckerPath-Signature') or request.headers.get('X-Signature')
    if not _verify_signature(raw, sig):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid signature')
    try:
        payload = json.loads(raw.decode('utf-8'))
    except Exception:
        raise HTTPException(status_code=400, detail='Invalid JSON')
    event = payload.get('event')
    return JSONResponse({'ok': True, 'received': True, 'event': event})