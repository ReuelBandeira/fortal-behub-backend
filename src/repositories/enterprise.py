from sqlalchemy.orm import Session
from src.models.enterprise import EnterpriseModel
from src.schemas.enterprise import EnterpriseCreate, EnterpriseUpdate
from typing import Optional
from datetime import datetime

class EnterpriseRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: EnterpriseCreate):
        enterprise = EnterpriseModel(**data.dict())
        self.db.add(enterprise)
        self.db.commit()
        self.db.refresh(enterprise)
        return enterprise

    def get_by_id(self, enterprise_id: int):
        return self.db.query(EnterpriseModel).filter(EnterpriseModel.id == enterprise_id).first()

    def get_all(
        self,
        enterprise: Optional[str] = None,
        address: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 10
    ):
        query = self.db.query(EnterpriseModel)

        if enterprise:
            query = query.filter(EnterpriseModel.enterprise.ilike(f"%{enterprise}%"))

        if address:
            query = query.filter(EnterpriseModel.address.ilike(f"%{address}%"))

        if start_time:
            query = query.filter(EnterpriseModel.start_time >= start_time)

        if end_time:
            query = query.filter(EnterpriseModel.end_time <= end_time)

        if is_active is not None:
            query = query.filter(EnterpriseModel.is_active == is_active)

        total = query.count()
        items = query.offset(skip).limit(limit).all()

        return total, items

    def update(self, enterprise_id: int, data: EnterpriseUpdate):
        enterprise = self.get_by_id(enterprise_id)
        if not enterprise:
            return None
        for field, value in data.dict(exclude_unset=True).items():
            setattr(enterprise, field, value)
        self.db.commit()
        self.db.refresh(enterprise)
        return enterprise

    def soft_delete(self, enterprise_id: int):
        enterprise = self.get_by_id(enterprise_id)
        if not enterprise:
            return None
        enterprise['is_active'] = False
        self.db.delete(enterprise)
        self.db.commit()
        return enterprise