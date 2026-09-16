from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from sqlalchemy.sql import func
from app.database import Base
from app.schemas import WorkMode


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    department = Column(String(100), nullable=False)
    primary_skill = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    work_mode = Column(Enum(WorkMode), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
