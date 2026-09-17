from datetime import datetime
from app.schemas import EmployeeEdit
from app.schemas import EmployeeInput
from sqlalchemy import func
from sqlalchemy.orm import Session
from app import models, schemas

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
    except Exception as e:
        db.rollback()
        raise e


# Function to get all employees
def fetch_all_employees(db:Session):
    return db.query(models.Employee).all()


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
    except Exception as e:
        db.rollback()
        raise e


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
