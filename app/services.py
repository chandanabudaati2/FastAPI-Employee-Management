from datetime import datetime
from app.schemas import EmployeeEdit
from app.schemas import EmployeeInput
from sqlalchemy import func
from sqlalchemy.orm import Session
from app import models, schemas

# Simple list to store all employee records in memory
employee_records = []

# Counter to generate employee ID starting from 1
emp_id_counter = 1


# Helper function to check if email is already taken
def is_email_taken(db: Session, email_to_check: str, current_emp_id: int | None = None) -> bool:
    query = db.query(models.Employee).filter(
        func.lower(models.Employee.email) == email_to_check.strip().lower()
    )
    if current_emp_id is not None:
        query = query.filter(models.Employee.id != current_emp_id)
    return query.first() is not None

# Function to add a new employee
def save_employee(emp_data: EmployeeInput):
    global emp_id_counter
    new_emp = {
        "id": emp_id_counter,
        "name": emp_data.name,
        "email": emp_data.email,
        "department": emp_data.department,
        "primary_skill": emp_data.primary_skill,
        "location": emp_data.location,
        "work_mode": emp_data.work_mode,
        "is_active": True,
        "created_at": datetime.now(),
    }
    employee_records.append(new_emp)
    emp_id_counter += 1
    return new_emp


# Function to get all employees
def fetch_all_employees():
    return employee_records


# Function to find employee by ID
def find_employee_by_id(emp_id: int):
    for emp in employee_records:
        if emp["id"] == emp_id:
            return emp
    return None


# Function to update employee details
def update_employee_record(emp_id: int, updated_info: EmployeeEdit):
    for emp in employee_records:
        if emp["id"] == emp_id:
            emp["name"] = updated_info.name
            emp["email"] = updated_info.email
            emp["department"] = updated_info.department
            emp["primary_skill"] = updated_info.primary_skill
            emp["location"] = updated_info.location
            emp["work_mode"] = updated_info.work_mode
            emp["is_active"] = updated_info.is_active
            return emp
    return None


# Function to delete employee by ID
def remove_employee(emp_id: int):
    for index, emp in enumerate(employee_records):
        if emp["id"] == emp_id:
            del employee_records[index]
            return True
    return False
