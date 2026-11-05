from fastapi import FastAPI, HTTPException, Path, Query, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app import models, schemas, services
from app.database import engine, get_db

# Initialize FastAPI app for Employee Service
app = FastAPI(
    title="Employee Service",
    description="Microservice responsible for managing employees.",
    version="1.0.0",
)

# Automatically create tables in employee_service_db on startup
models.Base.metadata.create_all(bind=engine)
@app.get("/", tags=["Home"], status_code=status.HTTP_200_OK)
def home():
    return {
        "message": "Welcome to the Employee Management API!",
        "version": "2.0.0",
        "docs": "/docs",
    }
# 1. Health check endpoint
@app.get("/health", tags=["Health"], status_code=status.HTTP_200_OK)
def check_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "service": "employee-service", "message": "Employee Service is healthy"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Employee Service database connection failed.",
        )


# 2. Create a new employee (POST /employees)
@app.post(
    "/employees",
    tags=["Employees"],
    response_model=schemas.EmployeeDetails,
    status_code=status.HTTP_201_CREATED,
)
def add_new_employee(
    emp_data: schemas.EmployeeInput,
    db: Session = Depends(get_db),
):
    if services.is_email_taken(db, emp_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{emp_data.email}' is already registered with another employee.",
        )
    return services.save_employee(db, emp_data)


# 3. List employees with filters and pagination (GET /employees)
@app.get(
    "/employees",
    tags=["Employees"],
    response_model=schemas.PaginatedEmployeeResponse,
    status_code=status.HTTP_200_OK,
)
def get_employees(
    search: str | None = Query(None, description="Search by employee name (partial, case-insensitive)"),
    department: str | None = Query(None, description="Filter by department"),
    work_mode: schemas.WorkMode | None = Query(None, description="Filter by work mode (WFH or WFO)"),
    is_active: bool | None = Query(None, description="Filter by active status (true or false)"),
    limit: int = Query(10, ge=1, le=100, description="Max records to return (1-100)"),
    offset: int = Query(0, ge=0, description="Records to skip (min 0)"),
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


# 4. Get a single employee by ID (GET /employees/{employee_id})
# Note: Called by Work Item Service to check employee existence
@app.get(
    "/employees/{employee_id}",
    tags=["Employees"],
    response_model=schemas.EmployeeDetails,
    status_code=status.HTTP_200_OK,
)
def get_employee_by_id(
    employee_id: int = Path(..., gt=0, description="The ID of the employee to get"),
    db: Session = Depends(get_db),
):
    emp = services.find_employee_by_id(db, employee_id)
    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )
    return emp
