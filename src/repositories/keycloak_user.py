from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.models.keycloak_user import KeycloakUserModel
from src.schemas.password_reset import KeycloakUserCreate, KeycloakUserUpdate
from typing import Optional
from datetime import datetime


class KeycloakUserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_keycloak_id(self, keycloak_user_id: str) -> Optional[KeycloakUserModel]:
        """
        Busca usuário pelo ID do Keycloak
        """
        return self.db.query(KeycloakUserModel).filter(
            KeycloakUserModel.keycloak_user_id == keycloak_user_id
        ).first()

    def get_by_email(self, email: str) -> Optional[KeycloakUserModel]:
        """
        Busca usuário pelo email
        """
        return self.db.query(KeycloakUserModel).filter(
            KeycloakUserModel.email == email.lower()
        ).first()

    def get_by_username(self, username: str) -> Optional[KeycloakUserModel]:
        """
        Busca usuário pelo username
        """
        return self.db.query(KeycloakUserModel).filter(
            KeycloakUserModel.username == username.lower()
        ).first()

    def create(self, data: KeycloakUserCreate) -> KeycloakUserModel:
        """
        Cria um novo usuário
        """
        try:
            db_user = KeycloakUserModel(
                keycloak_user_id=data.keycloak_user_id,
                email=data.email,
                username=data.username,
                first_name=data.first_name,
                last_name=data.last_name
            )
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError as e:
            self.db.rollback()
            if "keycloak_user_id" in str(e):
                raise ValueError("Usuário já existe no sistema")
            elif "email" in str(e):
                raise ValueError("Email já cadastrado")
            elif "username" in str(e):
                raise ValueError("Username já cadastrado")
            else:
                raise ValueError("Erro ao criar usuário")

    def update(self, user_id: str, data: KeycloakUserUpdate) -> Optional[KeycloakUserModel]:
        """
        Atualiza dados do usuário
        """
        db_user = self.db.query(KeycloakUserModel).filter(
            KeycloakUserModel.id == user_id
        ).first()
        
        if not db_user:
            return None

        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        db_user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_last_login(self, keycloak_user_id: str) -> Optional[KeycloakUserModel]:
        """
        Atualiza o timestamp do último login
        """
        db_user = self.get_by_keycloak_id(keycloak_user_id)
        if not db_user:
            return None

        db_user.update_last_login()
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def save_reset_code(self, email: str, reset_code: str, expires_at: datetime) -> Optional[KeycloakUserModel]:
        """
        Salva o código de reset para um usuário
        """
        db_user = self.get_by_email(email)
        if not db_user:
            return None

        db_user.reset_code = reset_code
        db_user.reset_code_expires_at = expires_at
        db_user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def clear_reset_code(self, email: str) -> Optional[KeycloakUserModel]:
        """
        Limpa o código de reset de um usuário
        """
        db_user = self.get_by_email(email)
        if not db_user:
            return None

        db_user.clear_reset_code()
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_by_reset_code(self, email: str, reset_code: str) -> Optional[KeycloakUserModel]:
        """
        Busca usuário por email e código de reset válido
        """
        db_user = self.get_by_email(email)
        if not db_user:
            return None

        if db_user.validate_reset_code(reset_code):
            return db_user
        
        return None 