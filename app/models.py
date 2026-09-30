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

    # Relationship to WorkItem
    work_items = relationship("WorkItem", back_populates="assigned_employee")

class WorkItem(Base):
    __tablename__ = "work_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    status = Column(Enum(WorkItemStatus), default=WorkItemStatus.TODO, nullable=False)
    priority = Column(Enum(WorkItemPriority), default=WorkItemPriority.MEDIUM, nullable=False)
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship to Employee
    assigned_employee = relationship("Employee", back_populates="work_items")