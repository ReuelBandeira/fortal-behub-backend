from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from pydantic import BaseModel, validator
from src.services.email_service import get_email_service
from src.utils.auth_decorator import require_auth, require_role
from src.schemas.email import EmailRequest, EmailResponse, EmailError
import traceback



router = APIRouter(prefix="/email", tags=["Email"])

@router.post("/send", response_model=EmailResponse, status_code=status.HTTP_200_OK)
async def send_email(
    email_request: EmailRequest,
    user_data: Dict[str, Any] = Depends(require_auth())
) -> EmailResponse:
    """
    Envia um email (requer autenticação)
    
    Args:
        email_request: Dados do email a ser enviado
        user_data: Dados do usuário autenticado
        
    Returns:
        EmailResponse: Confirmação do envio do email
    """
    try:
        email_service = get_email_service()
        response = email_service.send_email(email_request)
        return response
        
    except Exception as e:
        print(f"Erro ao enviar email: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao enviar email: {str(e)}"
        )

@router.post("/send-bulk", response_model=List[EmailResponse], status_code=status.HTTP_200_OK)
async def send_bulk_email(
    email_requests: List[EmailRequest],
    user_data: Dict[str, Any] = Depends(require_role("admin"))
) -> List[EmailResponse]:
    """
    Envia múltiplos emails em lote (requer role admin)
    
    Args:
        email_requests: Lista de emails a serem enviados
        user_data: Dados do usuário autenticado
        
    Returns:
        List[EmailResponse]: Lista de confirmações dos envios
    """
    try:
        if not email_requests or len(email_requests) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lista de emails não pode estar vazia"
            )
        
        if len(email_requests) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Máximo de 100 emails por lote"
            )
        
        email_service = get_email_service()
        responses = email_service.send_bulk_email(email_requests)
        return responses
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao enviar emails em lote: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao enviar emails em lote: {str(e)}"
        )





@router.get("/health", status_code=status.HTTP_200_OK)
async def email_health_check(
    user_data: Dict[str, Any] = Depends(require_auth())
) -> Dict[str, Any]:
    """
    Verifica a saúde do serviço de email (requer autenticação)
    
    Returns:
        Dict com status do serviço de email
    """
    try:
        email_service = get_email_service()
        # Tentar obter um token para verificar se a configuração está correta
        token = email_service._get_access_token()
        
        return {
            "status": "healthy",
            "service": "email",
            "message": "Serviço de email funcionando corretamente",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "email",
            "message": f"Erro no serviço de email: {str(e)}",
            "timestamp": "2024-01-01T00:00:00Z"
        } 