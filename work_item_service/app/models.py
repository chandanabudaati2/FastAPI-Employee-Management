import enum
from sqlalchemy import Column, Date, DateTime, Enum, Integer, String, Text
from sqlalchemy.sql import func
from app.database import Base


class WorkItemStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class WorkItemPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class WorkItem(Base):
    __tablename__ = "work_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    # Stored as a normal integer without foreign key constraint
    employee_id = Column(Integer, nullable=False, index=True)
    status = Column(Enum(WorkItemStatus), default=WorkItemStatus.TODO, nullable=False)
    priority = Column(Enum(WorkItemPriority), default=WorkItemPriority.MEDIUM, nullable=False)
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
