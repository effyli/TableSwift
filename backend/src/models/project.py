from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class ProjectBase(BaseModel):
    id: UUID
    name: str

class ProjectCreate(BaseModel):
    name: str
    file_path: str
    user_id: UUID

    class Config:
        from_attributes = True

class Project(ProjectBase):
    file_path: str
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
