from email_validator import validate_email
from sqlalchemy.exc import SQLAlchemyError
from fastapi import FastAPI, HTTPException, Path, status, Depends, Query
from sqlalchemy.orm import Session
from app import models, schemas, services, database
from app.database import engine, get_db
from sqlalchemy import text
import logging

# Configure logging
logger = logging.getLogger(__name__)

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
def check_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return {"status": "ok", "message": "Employee Management API is working!"}
    except SQLAlchemyError:
        logger.error("Database connection failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed. Please check your database connection.",
        )

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

# 8. Add work items
@app.post(
    "/work-items",
    tags=["Work Items"],
    response_model=schemas.WorkItemDetails,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new work item",
)
def add_new_work_item(
    item_data: schemas.WorkItemInput,
    db: Session = Depends(get_db)
):
    return services.save_work_item(db, item_data)

@app.get(
    "/work-items",
    tags = ["Work Items"],
    response_model = schemas.PaginatedWorkItemResponse,
    status_code=status.HTTP_200_OK
)
def get_work_items(
    search : str | None = Query(
        None, 
        title="Work Item Title Search", 
        description = "Search by work item title"
    ),
    employee_id: int | None = Query(
        None,
        gt=0,
        description="Filter work items by employee id",
    ),
    status: schemas.WorkItemStatus | None = Query(
        None,
        description = ""
    ),
    priority: schemas.WorkItemPriority | None = Query(
        None,
        description="Filter by work item priority",
    ),
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Maximum number of work items to return",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Number of records to skip",
    ),
    db: Session = Depends(get_db),
):
    return services.fetch_work_items_paginated(
        db=db,
        search=search,
        employee_id=employee_id,
        status=status,
        priority=priority,
        limit=limit,
        offset=offset,
    )

# 10. Get a single work _item by ID
@app.get(
    "/work-items/{work_item_id}",
    tags=["Work Items"],
    response_model=schemas.WorkItemDetails,
    status_code=status.HTTP_200_OK,
    description="Get a single work item by ID",
)
def get_work_item_by_id(
    work_item_id: int = Path(..., gt=0, description="The ID of the work item to retrieve"),
    db: Session = Depends(get_db)
):
    work_item = services.find_work_item_by_id(db,work_item_id)
    if not work_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work item with ID {work_item_id} not found",
        )
    return work_item

# 11. Update an existing work item by ID
@app.put(
    "/work-items/{work_item_id}",
    tags= ["Work Items"],
    response_model=schemas.WorkItemDetails,
    status_code=status.HTTP_200_OK,
    description="Update an existing work item by ID",
)
def update_work_item(
    updated_info: schemas.WorkItemEdit,
    work_item_id: int = Path(..., gt=0, description="The ID of the work item to update"),
    db: Session = Depends(get_db),
):
    return services.update_work_item_record(db,work_item_id,updated_info)

# 12. Delete a work item by ID
@app.delete(
    "/work-items/{work_item_id}",
    tags=["Work Items"],
    status_code=status.HTTP_200_OK,
    description="Delete a work item by ID",
)
def delete_work_item(
    work_item_id: int = Path(..., gt=0, description="The ID of the work item to delete"),
    db: Session = Depends(get_db)
):
    deleted = services.remove_work_item(db, work_item_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work item with ID {work_item_id} not found.",
        )
    return {"message": f"Work item with ID {work_item_id} deleted successfully."}