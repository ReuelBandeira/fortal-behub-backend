from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from src.services.auth_service import get_keycloak_service
from src.utils.auth_decorator import require_auth, optional_auth
from src.schemas.auth import (
    UserInfo,
    TokenResponse,
    RefreshTokenRequest,
    LogoutRequest,
    LogoutResponse,
    TokenValidationResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/user", response_model=UserInfo)
async def get_current_user(
    user_data: Dict[str, Any] = Depends(require_auth())
) -> UserInfo:
    """
    Obtém informações do usuário autenticado
    
    Returns:
        UserInfo: Informações do usuário logado
    """
    return UserInfo(
        sub=user_data.get("sub"),
        preferred_username=user_data.get("preferred_username"),
        email=user_data.get("email"),
        name=user_data.get("name"),
        roles=user_data.get("roles", []),
        token_data=user_data.get("token_data"),
        user_info=user_data.get("user_info")
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest
) -> TokenResponse:
    """
    Renova o access token usando o refresh token
    
    Args:
        request: RefreshTokenRequest contendo o refresh token
        
    Returns:
        TokenResponse: Novo access token e refresh token
    """
    try:
        keycloak_service = get_keycloak_service()
        token_info = keycloak_service.refresh_token(request.refresh_token)
        
        return TokenResponse(
            access_token=token_info.get("access_token"),
            refresh_token=token_info.get("refresh_token"),
            expires_in=token_info.get("expires_in", 300)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao renovar token: {str(e)}"
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: LogoutRequest
) -> LogoutResponse:
    """
    Faz logout do usuário invalidando o refresh token
    
    Args:
        request: LogoutRequest contendo o refresh token
        
    Returns:
        LogoutResponse: Confirmação do logout
    """
    try:
        keycloak_service = get_keycloak_service()
        keycloak_service.logout(request.refresh_token)
        return LogoutResponse()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no logout: {str(e)}"
        )


@router.post("/validate", response_model=TokenValidationResponse)
async def validate_token(
    user_data: Dict[str, Any] = Depends(optional_auth())
) -> TokenValidationResponse:
    """
    Valida se o token fornecido é válido
    
    Returns:
        TokenValidationResponse: Resultado da validação
    """
    if user_data is None:
        return TokenValidationResponse(
            valid=False,
            error="Token não fornecido ou inválido"
        )
    
    return TokenValidationResponse(
        valid=True,
        user_info=UserInfo(
            sub=user_data.get("sub"),
            preferred_username=user_data.get("preferred_username"),
            email=user_data.get("email"),
            name=user_data.get("name"),
            roles=user_data.get("roles", []),
            token_data=user_data.get("token_data"),
            user_info=user_data.get("user_info")
        )
    )


@router.get("/me", response_model=UserInfo)
async def get_me(
    user_data: Dict[str, Any] = Depends(require_auth())
) -> UserInfo:
    """
    Endpoint alternativo para obter informações do usuário autenticado
    
    Returns:
        UserInfo: Informações do usuário logado
    """
    return UserInfo(
        sub=user_data.get("sub"),
        preferred_username=user_data.get("preferred_username"),
        email=user_data.get("email"),
        name=user_data.get("name"),
        roles=user_data.get("roles", []),
        token_data=user_data.get("token_data"),
        user_info=user_data.get("user_info")
    ) 