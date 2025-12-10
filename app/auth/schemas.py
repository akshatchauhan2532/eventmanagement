# app/auth/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional


# --- USER CREATION --- #
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str



# --- USER LOGIN --- #
class UserLogin(BaseModel):
    username: str
    password: str


# --- RESPONSE SCHEMA --- #
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    

    class Config:
        from_attributes = True  # replaces orm_mode in Pydantic v2


# --- TOKEN SCHEMA --- #
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None
