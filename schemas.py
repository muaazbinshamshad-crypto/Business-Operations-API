from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    owner_id: int

    class Config:
        from_attributes = True
class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


class ServiceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    is_active: bool
    owner_id: int

    class Config:
        from_attributes = True
