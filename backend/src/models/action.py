from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID
from typing import List, Dict, Any
from .operation import Operation

class ActionBase(BaseModel):
    id: int
    project_id: UUID
    datetime: datetime
    operation: Optional[Operation] = None
    file_column: Optional[str] = None

class Action(ActionBase):
    description: Optional[str] = None
    labels: Optional[List[Dict[str, Any]]] = None
    code: Optional[List[str]] = None

    class Config:
        from_attributes = True

class ActionCreate(BaseModel):
    project_id: UUID
    