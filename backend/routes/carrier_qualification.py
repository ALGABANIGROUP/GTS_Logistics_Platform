from fastapi import APIRouter

router = APIRouter()

@router.get("/verify-carrier/{dot_number}")
def verify_carrier(dot_number: str):
    return {"dot_number": dot_number, "status": "Verified"}
