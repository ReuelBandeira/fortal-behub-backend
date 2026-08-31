from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Union
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def auth_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handler específico para exceções de autenticação
    """
    if exc.status_code in [401, 403]:
        logger.warning(f"Erro de autenticação: {exc.detail} - IP: {request.client.host}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error_code": "AUTH_ERROR",
                "path": str(request.url.path)
            },
            headers=exc.headers
        )
    
    # Para outros tipos de HTTPException, retorna a resposta padrão
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler para erros de validação de requisição
    """
    print(f"DEBUG: Erro de validação capturado: {exc.errors()}")
    logger.warning(f"Erro de validação: {exc.errors()} - IP: {request.client.host}")
    
    # Verificar se há erro relacionado a email
    for error in exc.errors():
        print(f"DEBUG: Verificando erro: {error}")
        if "email" in str(error).lower() or "to" in str(error).lower():
            print(f"DEBUG: Erro de email encontrado: {error}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail": "Um ou mais emails inválidos fornecidos",
                    "error_code": "EMAIL_VALIDATION_ERROR",
                    "path": str(request.url.path)
                }
            )
    
    print(f"DEBUG: Retornando erro genérico de validação")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Erro de validação dos dados",
            "errors": exc.errors(),
            "error_code": "VALIDATION_ERROR",
            "path": str(request.url.path)
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler para exceções gerais não tratadas
    """
    logger.error(f"Erro interno: {str(exc)} - IP: {request.client.host} - Path: {request.url.path}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Erro interno do servidor",
            "error_code": "INTERNAL_ERROR",
            "path": str(request.url.path)
        }
    )


def setup_exception_handlers(app):
    """
    Configura os handlers de exceção na aplicação FastAPI
    
    Args:
        app: Instância da aplicação FastAPI
    """
    # Handler para HTTPException (inclui erros de autenticação)
    app.add_exception_handler(HTTPException, auth_exception_handler)
    
    # Handler para StarletteHTTPException (para compatibilidade)
    app.add_exception_handler(StarletteHTTPException, auth_exception_handler)
    
    # Handler para erros de validação
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # Handler para exceções gerais (deve ser o último)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Handlers de exceção configurados com sucesso")


class AuthMiddleware:
    """
    Middleware para logging de requisições de autenticação
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Log de requisições para endpoints de autenticação
            path = scope.get("path", "")
            if path.startswith("/auth"):
                logger.info(f"Requisição de autenticação: {scope.get('method')} {path}")
        
        await self.app(scope, receive, send) 