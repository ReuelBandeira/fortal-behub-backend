from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates
from sqlalchemy.sql import func
from src.config import Base
import uuid
import re
from datetime import datetime, timedelta
import hashlib
import secrets


class KeycloakUserModel(Base):
    __tablename__ = "keycloak_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    keycloak_user_id = Column(String, nullable=False, unique=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    username = Column(String, nullable=False, unique=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    reset_code = Column(String, nullable=True)
    reset_code_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)

    @validates('email')
    def validate_email(self, key, value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Email inválido")
        return value.lower()

    @validates('username')
    def validate_username(self, key, value):
        if not value or len(value.strip()) < 3:
            raise ValueError("Username deve ter pelo menos 3 caracteres")
        return value.lower()

    def generate_reset_code(self) -> str:
        """
        Gera um código de reset de 6 dígitos e atualiza o modelo
        """
        # Gerar código de 6 dígitos
        code = str(secrets.randbelow(900000) + 100000)  # 100000-999999
        
        # Hash do código para armazenamento seguro
        hashed_code = hashlib.sha256(code.encode()).hexdigest()
        
        # Definir expiração (20 minutos)
        expires_at = datetime.utcnow() + timedelta(minutes=20)
        
        # Atualizar modelo
        self.reset_code = hashed_code
        self.reset_code_expires_at = expires_at
        self.updated_at = datetime.utcnow()
        
        return code

    def validate_reset_code(self, code: str) -> bool:
        """
        Valida se o código fornecido é válido e não expirou
        """
        if not self.reset_code or not self.reset_code_expires_at:
            return False
        
        # Verificar se expirou
        if datetime.utcnow() > self.reset_code_expires_at:
            return False
        
        # Verificar se o código hash corresponde
        hashed_code = hashlib.sha256(code.encode()).hexdigest()
        return hashed_code == self.reset_code

    def clear_reset_code(self):
        """
        Limpa o código de reset
        """
        self.reset_code = None
        self.reset_code_expires_at = None
        self.updated_at = datetime.utcnow()

    def update_last_login(self):
        """
        Atualiza o timestamp do último login
        """
        self.last_login = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def is_reset_code_expired(self) -> bool:
        """
        Verifica se o código de reset expirou
        """
        if not self.reset_code_expires_at:
            return True
        return datetime.utcnow() > self.reset_code_expires_at 