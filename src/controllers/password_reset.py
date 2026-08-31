from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from src.config import get_db
from src.schemas.password_reset import (
    PasswordResetRequest, 
    PasswordResetResponse, 
    PasswordResetCodeRequest,
    PasswordResetCodeValidationRequest
)
from src.services.password_reset_service import PasswordResetService
from src.utils.auth_decorator import require_auth
from typing import Dict, Any
import traceback
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Password Reset"])


@router.post("/request-password-reset", response_model=PasswordResetResponse, status_code=status.HTTP_200_OK)
async def request_password_reset(
    request_data: PasswordResetRequest,
    db: Session = Depends(get_db),
    http_request: Request = None
):
    """
    Solicita reset de senha enviando código por email
    
    Args:
        request_data: Dados da requisição (email)
        db: Sessão do banco de dados
        http_request: Objeto da requisição HTTP
        
    Returns:
        PasswordResetResponse: Confirmação do envio do código
    """
    try:
        # Log da tentativa de reset
        client_ip = http_request.client.host if http_request else "unknown"
        logger.info(f"Tentativa de reset de senha para {request_data.email} - IP: {client_ip}")
        
        # Inicializar serviço
        password_reset_service = PasswordResetService(db)
        
        # Solicitar reset
        success, message = password_reset_service.request_password_reset(request_data.email)
        
        if success:
            logger.info(f"Reset de senha solicitado com sucesso para {request_data.email}")
            return PasswordResetResponse(
                message="Se o email fornecido estiver cadastrado, você receberá um código de verificação em breve."
            )
        else:
            logger.warning(f"Falha no reset de senha para {request_data.email}: {message}")
            # Por segurança, sempre retornar a mesma mensagem
            return PasswordResetResponse(
                message="Se o email fornecido estiver cadastrado, você receberá um código de verificação em breve."
            )
            
    except Exception as e:
        logger.error(f"Erro ao solicitar reset de senha: {str(e)}")
        traceback.print_exc()
        # Por segurança, sempre retornar a mesma mensagem
        return PasswordResetResponse(
            message="Se o email fornecido estiver cadastrado, você receberá um código de verificação em breve."
        )


@router.post("/validate-reset-code", status_code=status.HTTP_200_OK)
async def validate_reset_code(
    request_data: PasswordResetCodeValidationRequest,
    db: Session = Depends(get_db)
):
    """
    Valida código de reset de senha
    
    Args:
        request_data: Dados da requisição (email, código)
        db: Sessão do banco de dados
        
    Returns:
        Dict com resultado da validação
    """
    try:
        password_reset_service = PasswordResetService(db)
        
        # Validar código
        is_valid, message = password_reset_service.validate_reset_code(
            request_data.email, 
            request_data.code
        )
        
        if is_valid:
            return {
                "valid": True,
                "message": "Código válido"
            }
        else:
            return {
                "valid": False,
                "message": message
            }
            
    except Exception as e:
        logger.error(f"Erro ao validar código: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao validar código"
        )


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    request_data: PasswordResetCodeRequest,
    db: Session = Depends(get_db)
):
    """
    Reseta senha usando código de verificação
    
    Args:
        request_data: Dados da requisição (email, código, nova senha)
        db: Sessão do banco de dados
        
    Returns:
        Dict com resultado do reset
    """
    try:
        password_reset_service = PasswordResetService(db)
        
        # Resetar senha
        success, message = password_reset_service.reset_password_with_code(
            request_data.email,
            request_data.code,
            request_data.new_password
        )
        
        if success:
            logger.info(f"Senha resetada com sucesso para {request_data.email}")
            return {
                "success": True,
                "message": "Senha alterada com sucesso"
            }
        else:
            logger.warning(f"Falha ao resetar senha para {request_data.email}: {message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao resetar senha: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao resetar senha"
        )


@router.post("/clear-expired-codes", status_code=status.HTTP_200_OK)
async def clear_expired_codes(
    db: Session = Depends(get_db),
    user_data: Dict[str, Any] = Depends(require_auth())
):
    """
    Limpa códigos de reset expirados (requer autenticação)
    
    Args:
        db: Sessão do banco de dados
        user_data: Dados do usuário autenticado
        
    Returns:
        Dict com resultado da limpeza
    """
    try:
        password_reset_service = PasswordResetService(db)
        password_reset_service.clear_expired_codes()
        
        return {
            "message": "Códigos expirados limpos com sucesso"
        }
        
    except Exception as e:
        logger.error(f"Erro ao limpar códigos expirados: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao limpar códigos expirados"
        ) 