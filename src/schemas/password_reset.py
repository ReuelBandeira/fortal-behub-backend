from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime


class PasswordResetRequest(BaseModel):
    email: EmailStr

    @validator('email')
    def validate_email(cls, v):
        return v.lower()


class PasswordResetResponse(BaseModel):
    message: str
    timestamp: datetime = datetime.utcnow()


class PasswordResetCodeValidationRequest(BaseModel):
    email: EmailStr
    code: str

    @validator('email')
    def validate_email(cls, v):
        return v.lower()

    @validator('code')
    def validate_code(cls, v):
        if not v or len(v) != 6 or not v.isdigit():
            raise ValueError("Código deve ter exatamente 6 dígitos numéricos")
        return v


class PasswordResetCodeRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str

    @validator('email')
    def validate_email(cls, v):
        return v.lower()

    @validator('code')
    def validate_code(cls, v):
        if not v or len(v) != 6 or not v.isdigit():
            raise ValueError("Código deve ter exatamente 6 dígitos numéricos")
        return v

    @validator('new_password')
    def validate_password(cls, v):
        if not v or len(v) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres")
        return v


class KeycloakUserRead(BaseModel):
    id: str
    keycloak_user_id: str
    email: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class KeycloakUserCreate(BaseModel):
    keycloak_user_id: str
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @validator('email')
    def validate_email(cls, v):
        return v.lower()

    @validator('username')
    def validate_username(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError("Username deve ter pelo menos 3 caracteres")
        return v.lower()


class KeycloakUserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    last_login: Optional[datetime] = None 