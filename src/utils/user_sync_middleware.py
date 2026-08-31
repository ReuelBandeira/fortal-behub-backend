from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from src.config import get_db
from src.services.user_sync_service import UserSyncService
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class UserSyncMiddleware(BaseHTTPMiddleware):
    """
    Middleware para sincronizar automaticamente usuários do Keycloak
    """
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """
        Processa a requisição e sincroniza usuário se autenticado
        """
        # Processar a requisição primeiro
        response = await call_next(request)
        
        # Verificar se é uma requisição autenticada
        if self._should_sync_user(request):
            try:
                await self._sync_user_if_authenticated(request)
            except Exception as e:
                logger.error(f"Erro na sincronização de usuário: {str(e)}")
                # Não falhar a requisição por erro de sincronização
        
        return response
    
    def _should_sync_user(self, request: Request) -> bool:
        """
        Verifica se deve sincronizar usuário para esta requisição
        """
        # Sincronizar apenas para endpoints que requerem autenticação
        # Excluir endpoints de autenticação para evitar loops
        path = request.url.path
        
        # Endpoints que NÃO devem sincronizar
        exclude_paths = [
            "/auth/login",
            "/auth/request-password-reset",
            "/auth/reset-password",
            "/docs",
            "/openapi.json",
            "/favicon.ico"
        ]
        
        # Verificar se o path está na lista de exclusão
        for exclude_path in exclude_paths:
            if path.startswith(exclude_path):
                return False
        
        # Verificar se tem header de autorização
        auth_header = request.headers.get("authorization")
        return auth_header is not None and auth_header.startswith("Bearer ")
    
    async def _sync_user_if_authenticated(self, request: Request):
        """
        Sincroniza usuário se estiver autenticado
        """
        try:
            # Extrair token do header
            auth_header = request.headers.get("authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return
            
            token = auth_header.replace("Bearer ", "")
            
            # Validar token com Keycloak
            from src.services.auth_service import get_keycloak_service
            keycloak_service = get_keycloak_service()
            
            # Validar token e obter dados do usuário
            token_data = keycloak_service.validate_token(token)
            user_info = keycloak_service.get_user_info(token)
            
            # Combinar dados do token e informações do usuário
            user_data = {
                "sub": token_data.get("sub"),
                "email": user_info.get("email"),
                "preferred_username": user_info.get("preferred_username"),
                "given_name": user_info.get("given_name"),
                "family_name": user_info.get("family_name")
            }
            
            # Sincronizar usuário
            db = next(get_db())
            user_sync_service = UserSyncService(db)
            user_sync_service.ensure_user_exists(user_data)
            
            logger.info(f"Usuário sincronizado: {user_data.get('email')}")
            
        except Exception as e:
            logger.error(f"Erro ao sincronizar usuário: {str(e)}")
            # Não falhar a requisição por erro de sincronização 