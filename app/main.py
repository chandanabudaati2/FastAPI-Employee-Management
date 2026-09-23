from app import database
from fastapi import FastAPI, HTTPException, Path, status, Depends, Query
from sqlalchemy.orm import Session
from app import models, schemas, services
from app.database import engine, get_db

# Initialize FastAPI application
app = FastAPI(
    title="Employee Management API",
    description="A CRUD API for managing employee records with a database(MYSQL + SQLAlchemy).",
    version="2.0.0",
)

#create tables on startup
models.Base.metadata.create_all(bind=engine)

# 1. Home / Root endpoint
@app.get("/", tags=["Home"], status_code=status.HTTP_200_OK)
def home():
    return {
        "message": "Welcome to the Employee Management API!",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "employees": "/employees",
    }


# 2. Health check endpoint
@app.get("/health", tags=["Health"], status_code=status.HTTP_200_OK)
def check_health():
    return {"status": "ok", "message": "Employee Management API is working!"}


# 3. Create a new employee
@app.post(
    "/employees",
    tags=["Employees"],
    response_model=schemas.EmployeeDetails,
    status_code=status.HTTP_201_CREATED,
)
def add_new_employee(emp_data: schemas.EmployeeInput, db: Session = Depends(get_db)):
    if services.is_email_taken(db, emp_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{emp_data.email}' is already registered with another employee.",
        )
    return services.save_employee(db, emp_data)


# 4. Get all employees
@app.get(
    "/employees",
    tags=["Employees"],
    response_model=schemas.PaginatedEmployeeResponse,
    status_code=status.HTTP_200_OK,
)
def get_employees(
    search: str = Query(
        None, title="Employee Name Search",
        description="Search by employee name (partial match, case-insensitive)",
    ),
    department: str | None = Query(
        None,
        description="Filter employees by department",
    ),
    work_mode: schemas.WorkMode | None = Query(
        None,
        description="Filter by work mode (WFH or WFO)",
    ),
    is_active: bool | None = Query(
        None,
        description="Filter by active status (true or false)",
    ),
    limit: int = Query(
        10, ge=1, le=100,
        description="Maximum records to return. Allowed values: 1-100.",
    ),
    offset: int = Query(
        0, ge=0,
        description="Number of records to skip. Must not be negative.",
    ),
    db: Session = Depends(get_db),
):
    return services.fetch_employees_paginated(
        db=db,
        search=search,
        department=department,
        work_mode=work_mode,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )

# 5. Get a single employee by ID
@app.get(
    "/employees/{id}",
    tags=["Employees"],
    response_model=schemas.EmployeeDetails,
    status_code=status.HTTP_200_OK,
)
def get_employee_by_id(
    id: int = Path(..., gt=0, description="The ID of the employee to get"),
    db: Session = Depends(get_db)
):
    emp = services.find_employee_by_id(db,id)
    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {id} was not found.",
        )
    return emp


# 6. Update an existing employee
@app.put(
    "/employees/{id}",
    tags=["Employees"],
    response_model=schemas.EmployeeDetails,
    status_code=status.HTTP_200_OK,
)
def update_employee(
    emp_data: schemas.EmployeeEdit,
    db: Session = Depends(get_db),
    id: int = Path(..., gt=0, description="The ID of the employee to update"),
):
    emp = services.find_employee_by_id(db,id)
    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {id} was not found.",
        )

    if services.is_email_taken(db,emp_data.email, current_emp_id=id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{emp_data.email}' is already used.",
        )

    return services.update_employee_record(db,id, emp_data)


# 7. Delete an employee by ID
@app.delete(
    "/employees/{id}",
    tags=["Employees"],
    status_code=status.HTTP_200_OK,
)
def delete_employee(
    id: int = Path(..., gt=0, description="The ID of the employee to delete"),
    db: Session = Depends(get_db)
):
    deleted = services.remove_employee(db,id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {id} was not found.",
        )
    return {"message": f"Employee with ID {id} was deleted successfully."}
