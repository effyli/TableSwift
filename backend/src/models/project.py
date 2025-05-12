from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from .file import CreateFile, File
from typing import Optional, List
from .action import Action, ActionBase

class ProjectBase(BaseModel):
    id: UUID
    name: str

class ProjectCreate(BaseModel):
    name: str
    file_id: int
    file: CreateFile
    user_id: UUID

    class Config:
        from_attributes = True

class Project(ProjectBase):
    actions: List[ActionBase] = []
    active_action: Optional[Action] = None
    file: File
    created_at: datetime

    class Config:
        from_attributes = True
