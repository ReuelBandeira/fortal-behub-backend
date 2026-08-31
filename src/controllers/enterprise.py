from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from src.config import get_db
from src.schemas.enterprise import EnterpriseRead, EnterpriseCreate
from src.utils.pagination_response import PaginationResponse
from src.utils.auth_decorator import require_auth, require_role
from src.services.enterprise import EnterpriseService
from src.models.enterprise import EnterpriseModel
from sqlalchemy.exc import SQLAlchemyError
import traceback

router = APIRouter(prefix="/enterprise", tags=["Enterprise"])

@router.post("", response_model=EnterpriseCreate, status_code=status.HTTP_201_CREATED)
def create_enterprise(
    data: EnterpriseCreate,
    db: Session = Depends(get_db),
    user_data: Dict[str, Any] = Depends(require_auth())
):
    """
    Cria uma nova empresa (requer autenticação)
    """
    try:
        existing_cnpj = db.query(EnterpriseModel).filter(EnterpriseModel.cnpj == data.cnpj).first()
        if existing_cnpj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CNPJ já cadastrado."
            )
        existing_email = db.query(EnterpriseModel).filter(EnterpriseModel.email == data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado."
            )
        existing_telephone = db.query(EnterpriseModel).filter(EnterpriseModel.telephone == data.telephone).first()
        if existing_telephone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Telefone já cadastrado."
            )
        return EnterpriseService(db).create(
            data=data
        )
    except SQLAlchemyError as e:
        db.rollback()
        print("Erro no banco de dados:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno no banco de dados.")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print("Erro inesperado:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno inesperado.")


@router.get("", response_model=PaginationResponse[EnterpriseRead], status_code=status.HTTP_200_OK)
def filter_enterprises(
    enterprise: Optional[str] = Query(None),
    address: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    is_active: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    user_data: Dict[str, Any] = Depends(require_auth())
):
    """
    Lista empresas com filtros (requer autenticação)
    """
    try:
        return EnterpriseService(db).get_all(
            enterprise=enterprise,
            address=address,
            start_time=start_time,
            end_time=end_time,
            is_active=is_active,
            page=page,
            limit=limit
        )
    except SQLAlchemyError as e:
        db.rollback()
        print("Erro no banco de dados:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno no banco de dados.")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        print("Erro inesperado:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno inesperado.")

@router.get("/{enterprise_id}", response_model=EnterpriseRead, status_code=status.HTTP_200_OK)
def get_enterprise_by_id(
    enterprise_id: int,
    db: Session = Depends(get_db),
    user_data: Dict[str, Any] = Depends(require_auth())
):
    """
    Obtém uma empresa por ID (requer autenticação)
    """
    try:
        enterprise = EnterpriseService(db).get_by_id(enterprise_id)
        if not enterprise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Empresa com ID {enterprise_id} não encontrada."
            )
        return enterprise
    except SQLAlchemyError as e:
        db.rollback()
        print("Erro no banco de dados ao buscar empresa por ID:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno no banco de dados.")
    except Exception as e:
        print("Erro inesperado ao buscar empresa por ID:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno inesperado.")