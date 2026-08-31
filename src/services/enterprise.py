from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from src.repositories.enterprise import EnterpriseRepository
from src.schemas.enterprise import EnterpriseCreate, EnterpriseUpdate, EnterpriseRead
from src.utils.pagination_response import PaginationResponse

class EnterpriseService:
    def __init__(self, db: Session):
        self.repository = EnterpriseRepository(db)

    def get_all(
        self,
        enterprise: Optional[str] = None,
        address: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        limit: int = 10
    ) -> PaginationResponse[EnterpriseRead]:
        skip = (page - 1) * limit
        total, items = self.repository.get_all(
            enterprise=enterprise,
            address=address,
            start_time=start_time,
            end_time=end_time,
            is_active=is_active,
            skip=skip,
            limit=limit
        )
        # Converter modelos SQLAlchemy para schemas Pydantic
        enterprise_reads = []
        for item in items:
            try:
                # Converter objeto SQLAlchemy para dicionário
                item_dict = {
                    'id': item.id,
                    'enterprise': item.enterprise,
                    'address': item.address,
                    'cnpj': item.cnpj,
                    'rental_type': item.rental_type,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'telephone': item.telephone,
                    'email': item.email,
                    'is_active': item.is_active,
                    'created_at': item.created_at,
                    'updated_at': item.updated_at
                }
                enterprise_reads.append(EnterpriseRead.model_validate(item_dict))
            except Exception as e:
                print(f"Erro ao converter item {item.id}: {e}")
                # Pular item com erro
                continue
        return PaginationResponse[EnterpriseRead].create(
            items=enterprise_reads,
            total=total,
            page=page,
            limit=limit
        )

    def get_by_id(self, enterprise_id: int):
        return self.repository.get_by_id(enterprise_id)

    def create(self, data: EnterpriseCreate):
        return self.repository.create(data)

    def update(self, enterprise_id: int, data: EnterpriseUpdate):
        return self.repository.update(enterprise_id, data)

    def soft_delete(self, enterprise_id: int):
        return self.repository.soft_delete(enterprise_id)
