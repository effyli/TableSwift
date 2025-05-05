from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: UUID

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    user_id: Optional[UUID] = None
    email: Optional[str] = None
