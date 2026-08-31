from pydantic import BaseModel, EmailStr, validator, Field
from typing import Literal, Optional
from datetime import datetime
from validate_docbr import CNPJ

class EnterpriseSchema(BaseModel):
    enterprise: str
    address: str
    cnpj: str
    rental_type: Optional[Literal["INTERNO", "COWORKING", "AMBOS"]] = None
    start_time: datetime
    end_time: datetime
    telephone: str
    email: EmailStr
    is_active: bool
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    @validator("cnpj")
    def validate_cnpj(cls, value):
        if value and not CNPJ().validate(value):
            raise ValueError("CNPJ inválido")
        return value

class EnterpriseCreate(EnterpriseSchema):
    pass

class EnterpriseRead(EnterpriseSchema):
    id: int

    class Config:
        from_attributes = True

class EnterpriseUpdate(BaseModel):
    enterprise: Optional[str]
    address: Optional[str]
    cnpj: Optional[str]
    rental_type: Optional[Literal["INTERNO", "COWORKING", "AMBOS"]]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    telephone: Optional[str]
    email: Optional[EmailStr]
    is_active: Optional[bool]
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)