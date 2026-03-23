from __future__ import annotations
from typing import List, Optional, Literal, Any, Dict, Union
import os
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, validator
import httpx
try:
    from backend.integrations.loadboards.ExternalLoadBoardAgent import ExternalLoadBoardAgent
except Exception:
    try:
        from integrations.loadboards.ExternalLoadBoardAgent import ExternalLoadBoardAgent
    except Exception:
        ExternalLoadBoardAgent = None
try:
    from backend.integrations.loadboards.registry import get_provider
except Exception:
    try:
        from integrations.loadboards.registry import get_provider
    except Exception:
        get_provider = None

async def _noop_broadcast(*args, **kwargs) -> None:
    return None
broadcast_event = _noop_broadcast
try:
    from backend.routes.ws_routes import broadcast_event as _broadcast_event
    broadcast_event = _broadcast_event
except Exception:
    try:
        from backend.routes.ws_routes import broadcast_event as _broadcast_event
        broadcast_event = _broadcast_event
    except Exception:
        pass
router = APIRouter(prefix='/ai/freight-broker', tags=['AI Freight Broker'])

class BrokerRunRequest(BaseModel):
    user_id: int = Field(..., description='Owner user_id required by shipments API')
    source: Literal['ai', 'truckerpath', 'mixed'] = 'ai'
    limit: int = 5
    auto_post_truckerpath: bool = True
    preferences: Dict[str, Any] = Field(default_factory=dict)

    @validator('limit')
    def _limit_guard(cls, v: int) -> int:
        return max(1, min(v, 50))

class CreatedShipment(BaseModel):
    id: int
    pickup_location: Optional[str] = None
    dropoff_location: Optional[str] = None

class BrokerRunResult(BaseModel):
    message: str
    shipment_ids: List[int]
    posted_to_truckerpath: int = 0
    failed_postings: int = 0
    errors: List[str] = Field(default_factory=list)
INTERNAL_BASE_URL = os.getenv('INTERNAL_BASE_URL', 'http://localhost:8000')
SHIPMENT_CREATE_ENDPOINTS = ['/api/v1/shipments/shipments/']

def _to_float_or_none(value: Union[str, float, int, None]) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).strip())
    except Exception:
        return None

def _normalize_load_for_shipment_create(load: Dict[str, Any], user_id: int) -> Dict[str, Any]:
    pickup = load.get('pickup') or load.get('origin') or load.get('pickup_location') or load.get('pickup_city') or 'Unknown Pickup'
    dropoff = load.get('dropoff') or load.get('destination') or load.get('dropoff_location') or load.get('dropoff_city') or 'Unknown Dropoff'
    latitude = load.get('pickup_latitude') or load.get('latitude')
    longitude = load.get('pickup_longitude') or load.get('longitude')
    payload: Dict[str, Any] = {'pickup_location': pickup, 'dropoff_location': dropoff, 'user_id': user_id, 'trailer_type': load.get('trailer_type') or load.get('equipment') or load.get('equipment_type'), 'rate': _to_float_or_none(load.get('rate') or load.get('rate_usd') or load.get('price')), 'weight': load.get('weight'), 'length': load.get('length'), 'load_size': load.get('load_size'), 'description': load.get('description') or load.get('notes'), 'status': load.get('status') or 'Draft', 'latitude': _to_float_or_none(latitude), 'longitude': _to_float_or_none(longitude), 'recurring_type': load.get('recurring_type'), 'days': load.get('days')}
    return {k: v for (k, v) in payload.items() if v is not None}

async def _create_shipment_via_internal_api(client: httpx.AsyncClient, payload: Dict[str, Any]) -> CreatedShipment:
    last_error = None
    for path in SHIPMENT_CREATE_ENDPOINTS:
        url = INTERNAL_BASE_URL.rstrip('/') + path
        try:
            resp = await client.post(url, json=payload, timeout=30.0)
            if resp.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED):
                data = resp.json()
                sid = data.get('id') or data.get('shipment_id') or data.get('data', {}).get('id')
                if sid is None:
                    last_error = f'Create OK but no ID in response from {path}'
                    continue
                return CreatedShipment(id=int(sid), pickup_location=data.get('pickup_location') or payload.get('pickup_location'), dropoff_location=data.get('dropoff_location') or payload.get('dropoff_location'))
            else:
                last_error = f'{path} -> {resp.status_code}: {resp.text}'
        except Exception as e:
            last_error = f'{path} -> exception: {e}'
    raise RuntimeError(last_error or 'Unknown error creating shipment')

async def _post_to_truckerpath_via_provider(agent_load: Dict[str, Any], created: CreatedShipment) -> bool:
    if get_provider is None:
        return False
    try:
        ProviderClass = get_provider('truckerpath')
        provider = ProviderClass()
    except Exception:
        return False
    payload = {'company_id': os.getenv('TRUCKERPATH_COMPANY_ID', 'unknown'), 'contact_info': {'contact_email': os.getenv('TRUCKERPATH_CONTACT_EMAIL', 'ops@example.com'), 'contact_first_name': os.getenv('TRUCKERPATH_CONTACT_FIRST', 'Ops'), 'contact_last_name': os.getenv('TRUCKERPATH_CONTACT_LAST', 'Team'), 'contact_phone_number': os.getenv('TRUCKERPATH_CONTACT_PHONE', '+10000000000'), 'contact_phone_ext': os.getenv('TRUCKERPATH_CONTACT_EXT', '')}, 'shipment_info': {'equipment': [agent_load.get('trailer_type') or agent_load.get('equipment') or 'Dry Van'], 'load_size': agent_load.get('load_size') or 'FULL', 'description': agent_load.get('description') or agent_load.get('notes'), 'shipment_weight': agent_load.get('weight'), 'shipment_dimensions': {}, 'requirements': agent_load.get('requirements'), 'stop_list': [{'type': 'PICKUP', 'state': agent_load.get('pickup_state'), 'city': agent_load.get('pickup_city') or agent_load.get('origin') or '', 'address': agent_load.get('pickup_address'), 'lat': agent_load.get('pickup_latitude'), 'lng': agent_load.get('pickup_longitude'), 'date_local': agent_load.get('pickup_date')}, {'type': 'DROPOFF', 'state': agent_load.get('dropoff_state'), 'city': agent_load.get('dropoff_city') or agent_load.get('destination') or '', 'address': agent_load.get('dropoff_address'), 'lat': agent_load.get('dropoff_latitude'), 'lng': agent_load.get('dropoff_longitude'), 'date_local': agent_load.get('dropoff_date')}]}}
    try:
        res = await provider.post_load(payload)
        return bool(res and res.get('ok', False))
    except Exception:
        return False

async def _fetch_source_loads(req: BrokerRunRequest) -> List[Dict[str, Any]]:
    loads: List[Dict[str, Any]] = []
    if req.source in ('truckerpath', 'mixed') and get_provider is not None:
        try:
            ProviderClass = get_provider('truckerpath')
            provider = ProviderClass()
            live = await provider.list_loads(limit=req.limit)
            if isinstance(live, dict) and live.get('ok'):
                loads.extend(list(live.get('loads') or []))
        except Exception:
            pass
    if req.source in ('ai', 'mixed') and ExternalLoadBoardAgent is not None:
        try:
            ai_loads = ExternalLoadBoardAgent.fetch(source='ai', preferences={**req.preferences, 'limit': req.limit}) or []
            loads.extend(ai_loads)
        except Exception:
            pass
    return loads[:req.limit] if loads else []

@router.post('/run', response_model=BrokerRunResult)
async def run_ai_freight_broker(req: BrokerRunRequest) -> BrokerRunResult:
    """
    1) Fetch loads (provider and/or AI)
    2) Create internal shipments
    3) Optionally post to TruckerPath
    4) Broadcast WS event for UI updates
    """
    raw_loads = await _fetch_source_loads(req)
    if not raw_loads:
        raise HTTPException(status_code=400, detail='No loads returned')
    shipment_ids: List[int] = []
    posted_ok = 0
    posted_fail = 0
    errors: List[str] = []
    async with httpx.AsyncClient() as client:
        for item in raw_loads:
            try:
                created = await _create_shipment_via_internal_api(client, _normalize_load_for_shipment_create(item, user_id=req.user_id))
                shipment_ids.append(created.id)
            except Exception as e:
                errors.append(f'create_shipment: {e}')
                continue
            if req.auto_post_truckerpath:
                ok = await _post_to_truckerpath_via_provider(item, created)
                if ok:
                    posted_ok += 1
                else:
                    posted_fail += 1
            try:
                await broadcast_event(channel='events.freight_broker.created', payload={'shipment_id': created.id, 'pickup': created.pickup_location, 'dropoff': created.dropoff_location})
            except Exception:
                pass
    msg = f'Created {len(shipment_ids)} shipment(s). Posted {posted_ok} to TruckerPath ({posted_fail} failed).'
    return BrokerRunResult(message=msg, shipment_ids=shipment_ids, posted_to_truckerpath=posted_ok, failed_postings=posted_fail, errors=errors)
