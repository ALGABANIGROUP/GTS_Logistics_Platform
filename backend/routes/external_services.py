from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def external_services():
    return {"message": "External services running"}
