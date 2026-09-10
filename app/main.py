# pyrefly: ignore [missing-import]
from fastapi import FastAPI, HTTPException, Path, status
from app.models import EmployeeInput, EmployeeEdit, EmployeeDetails
from app.services import (
    is_email_taken,
    save_employee,
    fetch_all_employees,
    find_employee_by_id,
    update_employee_record,
    remove_employee,
)

# Initialize FastAPI application
app = FastAPI(
    title="Employee Management API",
    description="A simple in-memory CRUD API for managing employee records without a database.",
    version="1.0.0",
)


# 1. Home / Root endpoint
@app.get("/", tags=["Home"], status_code=status.HTTP_200_OK)
def home():
    return {
        "message": "Welcome to the Employee Management API!",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "employees": "/employees",
    }


# 2. Health check endpoint
@app.get("/health", tags=["Health"], status_code=status.HTTP_200_OK)
def check_health():
    return {"status": "ok", "message": "Employee Management API is working!"}


# 2. Create a new employee
@app.post(
    "/employees",
    tags=["Employees"],
    response_model=EmployeeDetails,
    status_code=status.HTTP_201_CREATED,
)
def add_new_employee(emp_data: EmployeeInput):
    if is_email_taken(emp_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{emp_data.email}' is already registered with another employee.",
        )
    return save_employee(emp_data)


# 3. Get all employees
@app.get(
    "/employees",
    tags=["Employees"],
    response_model=list[EmployeeDetails],
    status_code=status.HTTP_200_OK,
)
def get_all_employees():
    return fetch_all_employees()


# 4. Get a single employee by ID
@app.get(
    "/employees/{id}",
    tags=["Employees"],
    response_model=EmployeeDetails,
    status_code=status.HTTP_200_OK,
)
def get_employee_by_id(
    id: int = Path(..., gt=0, description="The ID of the employee to get"),
):
    emp = find_employee_by_id(id)
    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {id} was not found.",
        )
    return emp


# 5. Update an existing employee
@app.put(
    "/employees/{id}",
    tags=["Employees"],
    response_model=EmployeeDetails,
    status_code=status.HTTP_200_OK,
)
def update_employee(
    emp_data: EmployeeEdit,
    id: int = Path(..., gt=0, description="The ID of the employee to update"),
):
    emp = find_employee_by_id(id)
    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {id} was not found.",
        )

    if is_email_taken(emp_data.email, current_emp_id=id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{emp_data.email}' is already used by another employee.",
        )

    return update_employee_record(id, emp_data)


# 6. Delete an employee by ID
@app.delete(
    "/employees/{id}",
    tags=["Employees"],
    status_code=status.HTTP_200_OK,
)
def delete_employee(
    id: int = Path(..., gt=0, description="The ID of the employee to delete"),
):
    deleted = remove_employee(id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {id} was not found.",
        )
    return {"message": f"Employee with ID {id} was deleted successfully."}
