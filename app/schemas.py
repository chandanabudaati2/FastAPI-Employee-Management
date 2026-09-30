from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# Enum for work mode options
class WorkMode(str, Enum):
    WFH = "WFH"
    WFO = "WFO"

#Base schema 
class EmployeeBase(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    department: str = Field(..., min_length=1)
    primary_skill: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    work_mode: WorkMode

    # Reject whitespace-only values
    @field_validator("name", "department", "primary_skill", "location")
    @classmethod
    def reject_empty_or_whitespace(cls, value: str):
        if not value or not value.strip():
            raise ValueError("Field cannot be empty or contain only whitespace.")
        return value.strip()


# Schema for creating a new employee POST /employees
class EmployeeInput(EmployeeBase):
    pass

# Schema for updating an existing employee PUT /employees/{id}
class EmployeeEdit(EmployeeBase):
    is_active: bool = True

# Schema for returning employee details
class EmployeeDetails(BaseModel):
    id: int
    name: str
    email: EmailStr
    department: str
    primary_skill: str
    location: str
    work_mode: WorkMode
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Schema for paginated employee list response
class PaginatedEmployeeResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[EmployeeDetails]
    message: str | None = None

from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# --- Enums ---
class WorkItemStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class WorkItemPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# --- Nested Employee Schema for Work Item Response ---
class AssignedEmployee(BaseModel):
    id: int
    name: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


# --- Work Item Base Schema ---
class WorkItemBase(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the work item")
    description: str | None = Field(None, description="Detailed description")
    employee_id: int = Field(..., gt=0, description="Assigned employee ID")
    status: WorkItemStatus = Field(default=WorkItemStatus.TODO)
    priority: WorkItemPriority = Field(default=WorkItemPriority.MEDIUM)
    due_date: date | None = Field(None, description="Optional due date (YYYY-MM-DD)")

    @field_validator("title")
    @classmethod
    def reject_empty_or_whitespace_title(cls, value: str):
        if not value or not value.strip():
            raise ValueError("Title cannot be empty or contain only whitespace.")
        return value.strip()


# POST /work-items input
class WorkItemInput(WorkItemBase):
    pass


# PUT /work-items/{work_item_id} input
class WorkItemEdit(WorkItemBase):
    pass


# Response Schema for single work item
class WorkItemDetails(BaseModel):
    id: int
    title: str
    description: str | None = None
    employee_id: int
    status: WorkItemStatus
    priority: WorkItemPriority
    due_date: date | None = None
    created_at: datetime
    assigned_employee: AssignedEmployee
    model_config = ConfigDict(from_attributes=True)


# Response Schema for paginated list
class PaginatedWorkItemResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[WorkItemDetails]
    message: str | None = None
