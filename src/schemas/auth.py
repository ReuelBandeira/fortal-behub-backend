from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any


class UserInfo(BaseModel):
    """Schema para informações do usuário"""
    sub: str
    preferred_username: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    roles: List[str] = []
    token_data: Optional[Dict[str, Any]] = None
    user_info: Optional[Dict[str, Any]] = None


class TokenResponse(BaseModel):
    """Schema para resposta de token"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Schema para requisição de refresh token"""
    refresh_token: str


class LogoutRequest(BaseModel):
    """Schema para requisição de logout"""
    refresh_token: str


class LogoutResponse(BaseModel):
    """Schema para resposta de logout"""
    message: str = "Logout realizado com sucesso"


class AuthError(BaseModel):
    """Schema para erros de autenticação"""
    detail: str
    error_code: Optional[str] = None


class TokenValidationResponse(BaseModel):
    """Schema para resposta de validação de token"""
    valid: bool
    user_info: Optional[UserInfo] = None
    error: Optional[str] = None 