import os
import httpx
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from app import models, schemas

# Read Employee Service URL from environment variable
EMPLOYEE_SERVICE_URL = os.getenv("EMPLOYEE_SERVICE_URL", "http://localhost:8001").rstrip("/")


# 1. Helper function: Call Employee Service via HTTPX with 5s timeout
def verify_employee_exists(employee_id: int):
    url = f"{EMPLOYEE_SERVICE_URL}/employees/{employee_id}"
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(url)

        # Employee found
        if response.status_code == 200:
            return True

        # Employee does not exist in Employee Service
        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found",
            )

        # Any unexpected response from Employee Service
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Employee service returned unexpected status: {response.status_code}",
        )

    # Caught when Employee Service is stopped, connection refused, or timed out
    except (httpx.RequestError, httpx.TimeoutException):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Employee service is unavailable. Please ensure Employee Service is running on port 8001.",
        )


# 2. Create and save a new work item
def save_work_item(db: Session, item_data: schemas.WorkItemInput) -> models.WorkItem:
    # Rule: New work items must start with TODO
    if item_data.status in (schemas.WorkItemStatus.IN_PROGRESS, schemas.WorkItemStatus.COMPLETED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New work items must start with TODO status.",
        )

    # Verify employee exists via HTTP API call to Employee Service
    verify_employee_exists(item_data.employee_id)

    # Create model instance
    new_work_item = models.WorkItem(
        title=item_data.title,
        description=item_data.description,
        employee_id=item_data.employee_id,
        status=models.WorkItemStatus.TODO,
        priority=item_data.priority,
        due_date=item_data.due_date,
    )

    try:
        db.add(new_work_item)
        db.commit()
        db.refresh(new_work_item)
        return new_work_item
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while creating work item.",
        )


# 3. Retrieve work items with search, filters, and pagination
def fetch_work_items_paginated(
    db: Session,
    search: str | None = None,
    employee_id: int | None = None,
    status: schemas.WorkItemStatus | None = None,
    priority: schemas.WorkItemPriority | None = None,
    limit: int = 10,
    offset: int = 0,
):
    query = db.query(models.WorkItem)

    # Partial case-insensitive search by title
    if search and search.strip():
        query = query.filter(
            func.lower(models.WorkItem.title).like(f"%{search.strip().lower()}%")
        )

    # Filter by assigned employee
    if employee_id is not None:
        query = query.filter(models.WorkItem.employee_id == employee_id)

    # Filter by work item status
    if status is not None:
        query = query.filter(models.WorkItem.status == status)

    # Filter by priority
    if priority is not None:
        query = query.filter(models.WorkItem.priority == priority)

    # Pre-pagination count
    total = query.count()

    # Deterministic ascending order by ID, with offset and limit
    items = (
        query.order_by(models.WorkItem.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    message = None
    if not items:
        message = "No work items found matching your criteria."
    elif search or employee_id is not None or status is not None or priority is not None:
        message = f"Found {total} work item(s) matching your filters."
    else:
        message = "Work items fetched successfully."

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items,
        "message": message,
    }


# 4. Find work item by ID
def find_work_item_by_id(db: Session, work_item_id: int):
    return db.query(models.WorkItem).filter(models.WorkItem.id == work_item_id).first()
