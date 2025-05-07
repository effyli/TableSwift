from fastapi import APIRouter, Depends
from ..models.operation import Operation
from ..services.operation import get_operations
from typing import List
from ..dependencies import validate_token

router = APIRouter(
    prefix="/operation",
    tags=["operation"]
)

@router.get("/", response_model=List[Operation])
async def list_operations(_=Depends(validate_token)):
    """Get all available operations."""
    return get_operations()
