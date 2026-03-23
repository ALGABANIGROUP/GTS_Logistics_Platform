from pydantic import BaseModel, EmailStr, Field
from typing import Literal

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: Literal["admin", "user", "manager"]

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    role: str

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):  # ✅ API token payload
    access_token: str
    token_type: str = "bearer"
class TokenData(BaseModel):
    id: int
    role: str

# Password Reset Schemas
class ForgotPasswordIn(BaseModel):
    email: EmailStr

class ResetPasswordIn(BaseModel):
    token: str = Field(min_length=10)
    new_password: str = Field(min_length=8)

class ChangePasswordIn(BaseModel):
    old_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8)