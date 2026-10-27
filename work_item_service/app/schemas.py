from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator


class WorkItemStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class WorkItemPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class WorkItemBase(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the work item")
    description: str | None = Field(None, description="Detailed description")
    employee_id: int = Field(..., gt=0, description="Assigned employee ID")
    priority: WorkItemPriority = Field(default=WorkItemPriority.MEDIUM)
    due_date: date | None = Field(None, description="Optional due date (YYYY-MM-DD)")

    @field_validator("title")
    @classmethod
    def reject_empty_or_whitespace_title(cls, value: str):
        if not value or not value.strip():
            raise ValueError("Title cannot be empty or contain only whitespace.")
        return value.strip()


# Input schema for POST /work-items
class WorkItemInput(WorkItemBase):
    status: WorkItemStatus = Field(default=WorkItemStatus.TODO)


# Response schema for a single work item (flat, no nested assigned_employee)
class WorkItemDetails(BaseModel):
    id: int
    title: str
    description: str | None = None
    employee_id: int
    status: WorkItemStatus
    priority: WorkItemPriority
    due_date: date | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Response schema for paginated list
class PaginatedWorkItemResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[WorkItemDetails]
    message: str | None = None
