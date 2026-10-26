from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class WorkMode(str, Enum):
    WFH = "WFH"
    WFO = "WFO"


# Base schema with whitespace validations
class EmployeeBase(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    department: str = Field(..., min_length=1)
    primary_skill: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    work_mode: WorkMode

    @field_validator("name", "department", "primary_skill", "location")
    @classmethod
    def reject_empty_or_whitespace(cls, value: str):
        if not value or not value.strip():
            raise ValueError("Field cannot be empty or contain only whitespace.")
        return value.strip()


# Input schema for POST /employees
class EmployeeInput(EmployeeBase):
    pass


# Response schema for single employee
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


# Response schema for paginated list
class PaginatedEmployeeResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[EmployeeDetails]
    message: str | None = None
