from sqlalchemy import func
from sqlalchemy.orm import Session
from app import models, schemas
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


# Case-insensitive duplicate email check
def is_email_taken(db: Session, email_to_check: str) -> bool:
    query = db.query(models.Employee).filter(
        func.lower(models.Employee.email) == email_to_check.strip().lower()
    )
    return query.first() is not None


# Create and save a new employee
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
            detail=f"Email '{emp_data.email}' is already taken. Please use a unique email address.",
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred. Please try again later.",
        )


# Retrieve employees with search, filters, and pagination
def fetch_employees_paginated(
    db: Session,
    search: str | None = None,
    department: str | None = None,
    work_mode: schemas.WorkMode | None = None,
    is_active: bool | None = None,
    limit: int = 10,
    offset: int = 0,
):
    query = db.query(models.Employee)

    if search and search.strip():
        query = query.filter(func.lower(models.Employee.name).like(f"%{search.strip().lower()}%"))

    if department and department.strip():
        query = query.filter(models.Employee.department == department.strip())

    if work_mode is not None:
        query = query.filter(models.Employee.work_mode == work_mode)

    if is_active is not None:
        query = query.filter(models.Employee.is_active == is_active)

    total = query.count()

    items = (
        query.order_by(models.Employee.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    message = None
    if not items:
        message = "No employees found matching your criteria."
    elif search or department or work_mode or is_active is not None:
        message = f"Found {total} employee(s) matching your criteria."
    else:
        message = "Employee details fetched successfully."

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
        "message": message,
    }


# Find an employee by ID
def find_employee_by_id(db: Session, emp_id: int):
    return db.query(models.Employee).filter(models.Employee.id == emp_id).first()
