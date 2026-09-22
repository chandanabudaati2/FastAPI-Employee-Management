from datetime import datetime
from app.schemas import EmployeeEdit, EmployeeInput
from sqlalchemy import func
from sqlalchemy.orm import Session
from app import models, schemas
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


# Helper function to check if email is already taken & case-sensitive
def is_email_taken(db: Session, email_to_check: str, current_emp_id: int | None = None):
    query = db.query(models.Employee).filter(
        func.lower(models.Employee.email) == email_to_check.strip().lower()
    )
    if current_emp_id is not None:
        query = query.filter(models.Employee.id != current_emp_id)
    return query.first() is not None

# Function to add a new employee
def save_employee(db: Session, emp_data: schemas.EmployeeInput) -> models.Employee:
    new_emp = models.Employee(
        name=emp_data.name,
        email=emp_data.email,
        department=emp_data.department,
        primary_skill=emp_data.primary_skill,
        location=emp_data.location,
        work_mode=emp_data.work_mode,
        is_active=True,
    )
    try:
        db.add(new_emp)
        db.commit()
        db.refresh(new_emp)
        return new_emp
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{emp_data.email}' is already taken. Please use a unique email address."
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred. Please try again later."
        )


# Function to get all employees
# Function to get employees with search, filters, and pagination
def fetch_employees_paginated(
    db: Session, search: str | None = None, department: str | None = None,
    work_mode: schemas.WorkMode | None = None, is_active: bool | None = None,
    limit: int = 10, offset: int = 0,
):
    query = db.query(models.Employee)

    # 1. Partial case-insensitive search by employee name
    if search and search.strip():
        query = query.filter(
            func.lower(models.Employee.name).like(f"%{search.strip().lower()}%")
        )

    # 2. Filter by department (exact match, case-insensitive or trimmed)
    if department and department.strip():
        query = query.filter(models.Employee.department == department.strip())

    # 3. Filter by work mode (WFH or WFO)
    if work_mode is not None:
        query = query.filter(models.Employee.work_mode == work_mode)

    # 4. Filter by active status (True or False)
    if is_active is not None:
        query = query.filter(models.Employee.is_active == is_active)

    # 5. Count total matching records BEFORE applying offset and limit
    total = query.count()

    # 6. Order by ID ascending, then apply offset and limit directly in SQL
    items = (
        query.order_by(models.Employee.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
    }



# Function to find employee by ID
def find_employee_by_id(db:Session,emp_id: int):
    return db.query(models.Employee).filter(models.Employee.id == emp_id).first()


# Function to update employee details
def update_employee_record(db: Session, emp_id: int, updated_info: schemas.EmployeeEdit):
    emp = find_employee_by_id(db, emp_id)
    if emp is None:
        return None
    if updated_info.name is not None:
        emp.name = updated_info.name
    if updated_info.email is not None:
        emp.email = updated_info.email
    if updated_info.department is not None:
        emp.department = updated_info.department
    if updated_info.primary_skill is not None:
        emp.primary_skill = updated_info.primary_skill
    if updated_info.location is not None:
        emp.location = updated_info.location
    if updated_info.work_mode is not None:
        emp.work_mode = updated_info.work_mode
    if updated_info.is_active is not None:
        emp.is_active = updated_info.is_active
    
    try:
        db.commit()
        db.refresh(emp)
        return emp
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{updated_info.email}' is already taken. Please use a unique email address.",
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred. Please try again later.",
        )


# Function to delete employee by ID
def remove_employee(db: Session,emp_id: int):
    emp = find_employee_by_id(db, emp_id)
    if emp is None:
        return None
    try:
        db.delete(emp)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
