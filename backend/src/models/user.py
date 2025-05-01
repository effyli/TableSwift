from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: str

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    email: Optional[str] = None
