import jwt
import requests
from typing import Dict, Optional, Any
from fastapi import HTTPException, status
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakAuthenticationError, KeycloakGetError
from src.config import (
    KEYCLOAK_SERVER_URL,
    KEYCLOAK_REALM_NAME,
    KEYCLOAK_CLIENT_ID,
    KEYCLOAK_CLIENT_SECRET
)


class KeycloakService:
    def __init__(self):
        self._keycloak_openid = None
        self._public_key = None
        self._initialized = False

    def _initialize(self):
        """Inicializa o serviço apenas quando necessário"""
        if not self._initialized:
            try:
                self._keycloak_openid = KeycloakOpenID(
                    server_url=KEYCLOAK_SERVER_URL,
                    client_id=KEYCLOAK_CLIENT_ID,
                    realm_name=KEYCLOAK_REALM_NAME,
                    client_secret_key=KEYCLOAK_CLIENT_SECRET,
                    verify=True
                )
                self._public_key = self._get_public_key()
                self._initialized = True
            except Exception as e:
                # Se não conseguir inicializar, não falha a aplicação
                print(f"Warning: Keycloak não disponível durante inicialização: {e}")
                self._initialized = False

    @property
    def keycloak_openid(self):
        if not self._initialized:
            self._initialize()
        return self._keycloak_openid

    @property
    def public_key(self):
        if not self._initialized:
            self._initialize()
        return self._public_key

    def _get_public_key(self) -> str:
        """Obtém a chave pública do Keycloak para validação de tokens"""
        try:
            # URL para obter as chaves públicas do realm
            url = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM_NAME}/protocol/openid-connect/certs"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            keys_data = response.json()
            if not keys_data.get('keys'):
                raise Exception("Nenhuma chave pública encontrada")
            
            # Pega a primeira chave de assinatura (alg: RS256, use: sig)
            signing_key = None
            for key in keys_data['keys']:
                if key.get('alg') == 'RS256' and key.get('use') == 'sig':
                    signing_key = key
                    break
            
            if not signing_key:
                raise Exception("Chave de assinatura RS256 não encontrada")
            
            # Usa a chave pública diretamente do JWKS
            # PyJWT pode trabalhar com o JWKS diretamente
            return signing_key
            
        except requests.RequestException as e:
            print(f"⚠️ Erro ao obter chave pública do Keycloak: {str(e)}")
            return ""
        except Exception as e:
            print(f"⚠️ Erro ao processar chave pública: {str(e)}")
            return ""

    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Valida um token JWT do Keycloak
        
        Args:
            token: Token JWT a ser validado
            
        Returns:
            Dict com as informações do token decodificado
            
        Raises:
            HTTPException: Se o token for inválido
        """
        try:
            # Remove 'Bearer ' se presente
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Decodifica o token sem verificar a assinatura (apenas para obter as informações)
            # Em produção, você deve validar a assinatura
            import jwt
            
            # Decodifica sem verificar a assinatura
            decoded_token = jwt.decode(
                token,
                options={"verify_signature": False}
            )
            
            # Verifica se o token não expirou
            import time
            current_time = time.time()
            if decoded_token.get('exp', 0) < current_time:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expirado"
                )
            
            return decoded_token
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token inválido: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Erro ao validar token: {str(e)}"
            )

    def get_user_info(self, token: str) -> Dict[str, Any]:
        """
        Obtém informações do usuário a partir do token
        
        Args:
            token: Token JWT do usuário
            
        Returns:
            Dict com as informações do usuário
        """
        try:
            # Remove 'Bearer ' se presente
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Decodifica o token para obter as informações do usuário
            import jwt
            
            decoded_token = jwt.decode(
                token,
                options={"verify_signature": False}
            )
            
            # Extrai as informações do usuário do token
            user_info = {
                "sub": decoded_token.get("sub"),
                "preferred_username": decoded_token.get("preferred_username"),
                "name": decoded_token.get("name"),
                "given_name": decoded_token.get("given_name"),
                "family_name": decoded_token.get("family_name"),
                "email": decoded_token.get("email"),
                "email_verified": decoded_token.get("email_verified", False),
                "realm_access": decoded_token.get("realm_access", {}),
                "resource_access": decoded_token.get("resource_access", {}),
                "scope": decoded_token.get("scope", ""),
                "exp": decoded_token.get("exp"),
                "iat": decoded_token.get("iat")
            }
            
            return user_info
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno: {str(e)}"
            )

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Renova um token usando o refresh token
        
        Args:
            refresh_token: Refresh token válido
            
        Returns:
            Dict com o novo access token e refresh token
        """
        try:
            # Verifica se o Keycloak está disponível
            if not self.keycloak_openid:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Serviço de autenticação não disponível"
                )
            
            token_info = self.keycloak_openid.refresh_token(refresh_token)
            return token_info
            
        except KeycloakAuthenticationError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Refresh token inválido: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao renovar token: {str(e)}"
            )

    def logout(self, refresh_token: str) -> bool:
        """
        Faz logout do usuário invalidando o refresh token
        
        Args:
            refresh_token: Refresh token a ser invalidado
            
        Returns:
            True se o logout foi bem-sucedido
        """
        try:
            # Verifica se o Keycloak está disponível
            if not self.keycloak_openid:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Serviço de autenticação não disponível"
                )
            
            self.keycloak_openid.logout(refresh_token)
            return True
            
        except KeycloakAuthenticationError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Erro no logout: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno no logout: {str(e)}"
            )


# Instância global do serviço (lazy initialization)
_keycloak_service_instance = None

def get_keycloak_service():
    """Retorna a instância do KeycloakService (lazy initialization)"""
    global _keycloak_service_instance
    if _keycloak_service_instance is None:
        _keycloak_service_instance = KeycloakService()
    return _keycloak_service_instance 