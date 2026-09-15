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
    def reject_empty_or_whitespace(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Field cannot be empty or contain only whitespace.")
        return value.strip()


# Schema for creating a new employee
class EmployeeInput(EmployeeBase):
    pass

# Schema for updating an existing employee
class EmployeeEdit(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    department: str = Field(..., min_length=1)
    primary_skill: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    work_mode: WorkMode
    is_active: bool = True

    # Reject whitespace-only values
    @field_validator("name", "department", "primary_skill", "location")
    @classmethod
    def reject_empty_or_whitespace(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Field cannot be empty or contain only whitespace.")
        return value.strip()


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
