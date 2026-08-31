from functools import wraps
from typing import Dict, Any, Optional
from fastapi import HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.services.auth_service import get_keycloak_service

# Instância do HTTPBearer para extrair o token
security = HTTPBearer(auto_error=False)


def require_auth():
    """
    Decorator para proteger rotas que requerem autenticação.
    
    Retorna uma dependência que:
    1. Extrai o Bearer token do header Authorization
    2. Valida o token com Keycloak
    3. Retorna os dados do usuário autenticado
    
    Returns:
        Dict com os dados do usuário autenticado
        
    Raises:
        HTTPException: Se o token for inválido ou não fornecido
    """
    def auth_dependency(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> Dict[str, Any]:
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de autenticação não fornecido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = credentials.credentials
        
        try:
            # Obtém a instância do serviço
            keycloak_service = get_keycloak_service()
            
            # Valida o token
            token_data = keycloak_service.validate_token(token)
            
            # Obtém informações do usuário
            user_info = keycloak_service.get_user_info(token)
            
            # Combina dados do token e informações do usuário
            user_data = {
                "token_data": token_data,
                "user_info": user_info,
                "sub": token_data.get("sub"),  # ID do usuário
                "preferred_username": user_info.get("preferred_username"),
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "roles": token_data.get("realm_access", {}).get("roles", [])
            }
            
            return user_data
            
        except HTTPException:
            # Re-raise HTTPExceptions do serviço
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Erro de autenticação: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    return auth_dependency


def optional_auth():
    """
    Decorator para rotas que podem ter autenticação opcional.
    
    Retorna uma dependência que:
    1. Tenta extrair e validar o token se fornecido
    2. Retorna None se não houver token
    3. Retorna dados do usuário se token válido
    
    Returns:
        Dict com dados do usuário ou None se não autenticado
    """
    def optional_auth_dependency(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> Optional[Dict[str, Any]]:
        if not credentials:
            return None
        
        token = credentials.credentials
        
        try:
            # Obtém a instância do serviço
            keycloak_service = get_keycloak_service()
            
            # Valida o token
            token_data = keycloak_service.validate_token(token)
            
            # Obtém informações do usuário
            user_info = keycloak_service.get_user_info(token)
            
            # Combina dados do token e informações do usuário
            user_data = {
                "token_data": token_data,
                "user_info": user_info,
                "sub": token_data.get("sub"),  # ID do usuário
                "preferred_username": user_info.get("preferred_username"),
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "roles": token_data.get("realm_access", {}).get("roles", [])
            }
            
            return user_data
            
        except HTTPException:
            # Se houver erro de autenticação, retorna None
            return None
        except Exception:
            # Se houver qualquer outro erro, retorna None
            return None
    
    return optional_auth_dependency


def require_role(required_role: str):
    """
    Decorator para verificar se o usuário tem uma role específica.
    
    Args:
        required_role: Nome da role requerida
        
    Returns:
        Dependência que verifica a role do usuário
    """
    def role_dependency(user_data: Dict[str, Any] = Depends(require_auth())) -> Dict[str, Any]:
        user_roles = user_data.get("roles", [])
        
        if required_role not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' é necessária para acessar este recurso"
            )
        
        return user_data
    
    return role_dependency


def require_any_role(required_roles: list[str]):
    """
    Decorator para verificar se o usuário tem pelo menos uma das roles especificadas.
    
    Args:
        required_roles: Lista de roles aceitas
        
    Returns:
        Dependência que verifica as roles do usuário
    """
    def any_role_dependency(user_data: Dict[str, Any] = Depends(require_auth())) -> Dict[str, Any]:
        user_roles = user_data.get("roles", [])
        
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Uma das roles {required_roles} é necessária para acessar este recurso"
            )
        
        return user_data
    
    return any_role_dependency 