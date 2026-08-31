from sqlalchemy.orm import Session
from src.repositories.keycloak_user import KeycloakUserRepository
from src.schemas.password_reset import KeycloakUserCreate, KeycloakUserUpdate
from src.models.keycloak_user import KeycloakUserModel
from typing import Dict, Any, Optional
from datetime import datetime


class UserSyncService:
    def __init__(self, db: Session):
        self.repository = KeycloakUserRepository(db)

    def sync_user_from_keycloak(self, user_data: Dict[str, Any]) -> KeycloakUserModel:
        """
        Sincroniza dados do usuário do Keycloak com a tabela local
        
        Args:
            user_data: Dados do usuário vindos do Keycloak
            
        Returns:
            KeycloakUserModel: Usuário sincronizado
        """
        try:
            # Extrair dados do usuário
            keycloak_user_id = user_data.get("sub")
            email = user_data.get("email", "").lower()
            username = user_data.get("preferred_username", "").lower()
            first_name = user_data.get("given_name")
            last_name = user_data.get("family_name")
            
            if not keycloak_user_id or not email or not username:
                raise ValueError("Dados obrigatórios do usuário não fornecidos")
            
            # Verificar se usuário já existe
            existing_user = self.repository.get_by_keycloak_id(keycloak_user_id)
            
            if existing_user:
                # Usuário existe, apenas atualizar último login
                existing_user.update_last_login()
                self.repository.db.commit()
                return existing_user
            else:
                # Usuário não existe, criar novo
                user_create_data = KeycloakUserCreate(
                    keycloak_user_id=keycloak_user_id,
                    email=email,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                
                new_user = self.repository.create(user_create_data)
                return new_user
                
        except Exception as e:
            print(f"Erro ao sincronizar usuário: {str(e)}")
            raise ValueError(f"Falha na sincronização do usuário: {str(e)}")

    def get_user_by_keycloak_id(self, keycloak_user_id: str) -> Optional[KeycloakUserModel]:
        """
        Busca usuário pelo ID do Keycloak
        """
        return self.repository.get_by_keycloak_id(keycloak_user_id)

    def get_user_by_email(self, email: str) -> Optional[KeycloakUserModel]:
        """
        Busca usuário pelo email
        """
        return self.repository.get_by_email(email)

    def update_user_info(self, keycloak_user_id: str, user_info: Dict[str, Any]) -> Optional[KeycloakUserModel]:
        """
        Atualiza informações do usuário
        """
        update_data = KeycloakUserUpdate(
            first_name=user_info.get("given_name"),
            last_name=user_info.get("family_name")
        )
        
        user = self.repository.get_by_keycloak_id(keycloak_user_id)
        if not user:
            return None
            
        return self.repository.update(str(user.id), update_data)

    def ensure_user_exists(self, user_data: Dict[str, Any]) -> KeycloakUserModel:
        """
        Garante que o usuário existe na tabela local
        Se não existir, cria; se existir, apenas atualiza último login
        """
        return self.sync_user_from_keycloak(user_data) 