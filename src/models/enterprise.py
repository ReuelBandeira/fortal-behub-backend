from sqlalchemy import Column, Integer, DateTime, String, TIMESTAMP, Boolean
from sqlalchemy.orm import validates
from validate_docbr import CNPJ
from src.config import Base
import re

class EnterpriseModel(Base):
    __tablename__ = "enterprise"

    id = Column(Integer, primary_key=True, index=True)
    enterprise = Column(String, nullable=False)
    address = Column(String, nullable=False)
    cnpj = Column(String, nullable=True, unique=True)
    rental_type = Column(String, nullable=False)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP, nullable=False)
    telephone = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)

    @validates('email')
    def validate_email(self, key, value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Email inválido")
        return value

    @validates('cnpj')
    def validate_cnpj(self, key, value):
        if value and not CNPJ().validate(value):
            raise ValueError("CNPJ inválido")
        return value

    @validates('rental_type')
    def validate_rental_type(self, key, value):
        allowed = ["INTERNO", "COWORKING", "AMBOS"]
        if value not in allowed:
            raise ValueError("Tipo de aluguel inválido")
        return value