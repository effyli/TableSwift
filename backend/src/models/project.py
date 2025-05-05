from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class ProjectBase(BaseModel):
    name: str
    file_path: str
    user_id: UUID

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
