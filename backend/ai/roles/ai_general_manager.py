from __future__ import annotations
from typing import Optional, Literal, Any, Dict
from datetime import date
import inspect
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
router = APIRouter(prefix='/ai/gm', tags=['AI General Manager'])
try:
    from backend.services.report_service import compile_system_report
except Exception:
    try:
        from backend.services.report_service import compile_system_report
    except Exception:
        compile_system_report = None

class ReportRequest(BaseModel):
    period: Literal['today', 'week', 'month', 'custom'] = 'week'
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    format: Literal['json', 'markdown'] = 'json'
    include_kpis: bool = Field(default=True)

class ReportResponse(BaseModel):
    message: str
    period: str
    format: str
    report: Optional[Any] = None
    error: Optional[str] = None

@router.post('/run', response_model=ReportResponse)
async def run_ai_general_manager(req: ReportRequest) -> ReportResponse:
    if compile_system_report is None:
        return ReportResponse(message='Strategic report disabled (report_service missing)', period=req.period, format=req.format, report=None)
    kwargs: Dict[str, Any] = {}
    try:
        sig = inspect.signature(compile_system_report)
        supported = set(sig.parameters.keys())
        candidate = {'period': req.period, 'start_date': req.start_date, 'end_date': req.end_date, 'fmt': req.format, 'format': req.format, 'include_kpis': req.include_kpis}
        for (k, v) in candidate.items():
            if k in supported:
                kwargs[k] = v
    except Exception:
        kwargs = {}
    try:
        result = await compile_system_report(**kwargs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Report generation failed: {e}')
    return ReportResponse(message='Strategic report generated', period=req.period, format=req.format, report=result)

@router.get('/sample', response_model=ReportResponse)
async def sample_schema() -> ReportResponse:
    sample = {'kpis': {'shipments_total': 42, 'revenue_total': 125000.5, 'expenses_total': 73000.0, 'profit': 52000.5, 'on_time_rate': 0.92}, 'highlights': ['On-time delivery improved by 4% WoW.', 'Finance: expenses trending down due to vendor consolidation.'], 'risks': ['Two loads flagged as delayed > 6h.'], 'actions': ['Follow up with carrier X on route CA-NV.', 'Enable CSV dedupe in Finance import job.']}
    return ReportResponse(message='Sample report (static)', period='week', format='json', report=sample)