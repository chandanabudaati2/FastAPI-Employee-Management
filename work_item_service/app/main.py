from fastapi import FastAPI, HTTPException, Path, Query, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app import models, schemas, services
from app.database import engine, get_db

# Initialize FastAPI app for Work Item Service
app = FastAPI(
    title="Work Item Service",
    description="Microservice responsible for managing work items and tasks.",
    version="1.0.0",
)

# Automatically create tables in work_item_service_db on startup
models.Base.metadata.create_all(bind=engine)

@app.get("/", tags=["Home"], status_code=status.HTTP_200_OK)
def home():
    return {
        "message": "Welcome to the Work Item Management API!",
        "version": "1.0.0",
        "docs": "/docs",
    }
# 1. Health check endpoint (GET /health)
@app.get("/health", tags=["Health"], status_code=status.HTTP_200_OK)
def check_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "service": "work-item-service", "message": "Work Item Service is healthy"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Work Item Service database connection failed.",
        )


# 2. Create and assign a work item (POST /work-items)
@app.post(
    "/work-items",
    tags=["Work Items"],
    response_model=schemas.WorkItemDetails,
    status_code=status.HTTP_201_CREATED,
)
def create_new_work_item(
    item_data: schemas.WorkItemInput,
    db: Session = Depends(get_db),
):
    return services.save_work_item(db, item_data)


# 3. List work items with filters and pagination (GET /work-items)
@app.get(
    "/work-items",
    tags=["Work Items"],
    response_model=schemas.PaginatedWorkItemResponse,
    status_code=status.HTTP_200_OK,
)
def get_work_items(
    search: str | None = Query(None, description="Search by title (case-insensitive, partial match)"),
    employee_id: int | None = Query(None, gt=0, description="Filter by assigned employee ID"),
    status: schemas.WorkItemStatus | None = Query(None, description="Filter by status (TODO, IN_PROGRESS, COMPLETED)"),
    priority: schemas.WorkItemPriority | None = Query(None, description="Filter by priority (LOW, MEDIUM, HIGH)"),
    limit: int = Query(10, ge=1, le=100, description="Maximum records to return (1-100)"),
    offset: int = Query(0, ge=0, description="Number of records to skip (min 0)"),
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


# 4. Get a single work item by ID (GET /work-items/{work_item_id})
@app.get(
    "/work-items/{work_item_id}",
    tags=["Work Items"],
    response_model=schemas.WorkItemDetails,
    status_code=status.HTTP_200_OK,
)
def get_work_item_by_id(
    work_item_id: int = Path(..., gt=0, description="The ID of the work item to retrieve"),
    db: Session = Depends(get_db),
):
    work_item = services.find_work_item_by_id(db, work_item_id)
    if not work_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work item with ID {work_item_id} not found.",
        )
    return work_item
