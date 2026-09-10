from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field


# Enum for work mode options
class WorkMode(str, Enum):
    WFH = "WFH"
    WFO = "WFO"


# Schema for creating a new employee
class EmployeeInput(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    department: str = Field(..., min_length=1)
    primary_skill: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    work_mode: WorkMode


# Schema for updating an existing employee
class EmployeeEdit(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    department: str = Field(..., min_length=1)
    primary_skill: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    work_mode: WorkMode
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
