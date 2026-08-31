from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
from enum import Enum
import re

class EmailPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

class EmailRequest(BaseModel):
    to: List[str]
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    subject: str
    body: str
    html_body: Optional[str] = None
    priority: EmailPriority = EmailPriority.NORMAL
    attachments: Optional[List[str]] = None

    @validator('to', 'cc', 'bcc', pre=True, always=True)
    def validate_emails(cls, v):
        if v is None:
            return v
        
        if not isinstance(v, list):
            raise ValueError("Emails devem estar em uma lista")
        
        # Regex mais permissiva para validação de email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        for email in v:
            if not isinstance(email, str):
                raise ValueError(f"Email deve ser uma string: {email}")
            
            if not re.match(email_pattern, email.strip()):
                raise ValueError(f"Email inválido: {email}")
        
        return [email.strip().lower() for email in v]

    @validator('subject')
    def validate_subject(cls, v):
        if not v or not v.strip():
            raise ValueError("Assunto do email é obrigatório")
        if len(v) > 255:
            raise ValueError("Assunto do email deve ter no máximo 255 caracteres")
        return v.strip()

    @validator('body')
    def validate_body(cls, v):
        if not v or not v.strip():
            raise ValueError("Corpo do email é obrigatório")
        return v.strip()

class EmailResponse(BaseModel):
    message_id: str
    status: str
    sent_at: str
    recipients: List[str]

class EmailError(BaseModel):
    error: str
    details: Optional[str] = None