from fastapi import APIRouter
from backend.data.trailer_types import TRAILER_TYPES
from backend.data.canada_us_locations import CANADA_US_LOCATIONS

router = APIRouter(prefix="/api/v1/meta", tags=["meta"])

@router.get("/trailer-types")
def get_trailer_types():
    return {"trailer_types": TRAILER_TYPES}

@router.get("/locations")
def get_locations():
    return {"locations": CANADA_US_LOCATIONS}
