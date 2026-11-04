from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()

MOCK_PAYLOADS = {
    "status": "ok",
    "sample_records": [{"id": 1, "title": "Mock Record"}],
}

@router.get("/")
def get_root():
    return MOCK_PAYLOADS
