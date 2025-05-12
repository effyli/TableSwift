from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from .operation import Operation
from .labels import Labels

class ActionBase(BaseModel):
    id: int
    project_id: UUID
    datetime: datetime
    operation: Optional[Operation] = None
    file_column: Optional[str] = None

class Action(ActionBase):
    description: Optional[str] = None
    labels: List[Labels]

    class Config:
        from_attributes = True

class ActionCreate(BaseModel):
    project_id: UUID
    