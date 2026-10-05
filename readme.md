# Employee & Work Item Management API

A production-ready REST API to manage employees and their assigned work items, built using **FastAPI**, **SQLAlchemy**, and **MySQL**. Data is permanently stored in a relational database, persists across server restarts, and demonstrates one-to-many database relationships with referential integrity.

---

## Technologies Used

- **Language:** Python 3.12 / 3.14
- **Framework:** FastAPI
- **Database:** MySQL 8+
- **ORM:** SQLAlchemy 2.0
- **Driver:** PyMySQL & Cryptography
- **Validation:** Pydantic v2
- **Server:** Uvicorn

---

## Project Structure

```text
FastAPI-EmpManagement/
├── app/
│   ├── __init__.py
│   ├── database.py       # Engine, sessionmaker, Base, and get_db dependency
│   ├── models.py         # SQLAlchemy Employee & WorkItem ORM models with relationships
│   ├── schemas.py        # Pydantic schemas, enums, validators, and response envelopes
│   ├── services.py       # Database CRUD operations, business logic, and queries
│   └── main.py           # FastAPI routes, controllers, and dependency injection
├── Screenshots_Task1/    # Task 1 test screenshots
├── Screenshots_Task2/    # Task 2 test screenshots
├── Screenshots_Task3/    # Task 3 test screenshots
├── Screenshots_Task_4/   # Task 4 Swagger UI test screenshots
├── .env.example          # Environment template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Project Architecture & File Breakdown

The project follows a **layered separation-of-concerns** architecture where each file handles a distinct responsibility:

### 1. `app/database.py` — Database Engine & Session Management
* **Database Connection:** Constructs a secure MySQL connection string using `URL.create()` to safely encode special characters from environment variables.
* **Engine with Health Checks:** Configures SQLAlchemy's `create_engine` with `pool_pre_ping=True` to automatically detect and recover from dropped or idle database connections.
* **Session Lifecycle (`get_db`):** Implements a generator-based dependency (`yield`) that creates a unique `SessionLocal` instance for each incoming HTTP request and guarantees it is cleanly closed in a `finally` block to prevent connection leaks.
* **Declarative Base:** Instantiates `Base = declarative_base()`, which serves as the foundation class for all ORM models.

### 2. `app/models.py` — SQLAlchemy ORM Data Models
* **`Employee` Table (`employees`):**
  * `id`: Auto-incrementing, indexed primary key.
  * `name`, `department`, `primary_skill`, `location`: Required string fields (`nullable=False`).
  * `email`: Indexed unique string (`unique=True`) preventing duplicate email entries at the database level.
  * `work_mode`: Enforced by MySQL Enum constraint strictly accepting `WFH` or `WFO`.
  * `is_active`: Boolean flag indicating employment status (defaults to `True`).
  * `created_at`: Auto-timestamped using MySQL's server-side `func.now()`.
  * **Relationship:** `work_items = relationship("WorkItem", back_populates="assigned_employee")`
* **`WorkItem` Table (`work_items`):**
  * `id`: Auto-incrementing, indexed primary key.
  * `title`: Required title (`nullable=False`, string length 255).
  * `description`: Optional text field (`nullable=True`).
  * `employee_id`: Foreign key referencing `employees.id` (`nullable=False`, indexed).
  * `status`: Enum strictly accepting `TODO`, `IN_PROGRESS`, `COMPLETED` (defaults to `TODO`).
  * `priority`: Enum strictly accepting `LOW`, `MEDIUM`, `HIGH` (defaults to `MEDIUM`).
  * `due_date`: Optional date field (`nullable=True`).
  * `created_at`: Auto-timestamped using MySQL's server-side `func.now()`.
  * `updated_at`: Auto-timestamped using MySQL's server-side `func.now()`, updating on modifications.
  * **Relationship:** `assigned_employee = relationship("Employee", back_populates="work_items")`

### 3. `app/schemas.py` — Pydantic Request & Response Schemas
* **Data Transfer Objects (DTOs):** Enforces data validation rules for incoming requests and standardizes outgoing JSON responses.
* **Enums:**
  * `WorkMode`: `"WFH"`, `"WFO"`
  * `WorkItemStatus`: `"TODO"`, `"IN_PROGRESS"`, `"COMPLETED"`
  * `WorkItemPriority`: `"LOW"`, `"MEDIUM"`, `"HIGH"`
* **Input Sanitization & Custom Validators:**
  * `@field_validator` rejects empty or whitespace-only strings for text fields and titles.
  * `@field_validator("due_date")` ensures due dates cannot be set in the past.
* **Employee Schemas:** `EmployeeInput`, `EmployeeEdit`, `EmployeeDetails`, `PaginatedEmployeeResponse`.
* **Work Item Schemas:**
  * `AssignedEmployee`: Lightweight DTO (`id`, `name`, `email`) included inside every work item response.
  * `WorkItemInput`: Validates payload for creating and assigning a work item (`POST /work-items`).
  * `WorkItemEdit`: Validates payload for updating details or reassigning a work item (`PUT /work-items/{id}`).
  * `WorkItemDetails`: Serializes a single work item with nested `assigned_employee` via `from_attributes=True`.
  * `PaginatedWorkItemResponse`: Wraps work item lists into an envelope with metadata (`total`, `limit`, `offset`, `items`, and `message`).

### 4. `app/services.py` — Business Logic & Database Queries
* **Decoupled Business Logic:** Encapsulates all database queries and transactions, keeping route handlers lean and focused solely on HTTP handling.
* **Employee Management:** Duplicate email checks, paginated queries, find by ID, update, and safe deletion with conflict checks.
* **Work Item Management:**
  * `save_work_item`: Validates assignee exists and is active before creating a work item.
  * `fetch_work_items_paginated`: Executes dynamic SQL filtering (title search, employee, status, priority), pre-pagination count, ascending ordering by ID, and SQL-level limit/offset.
  * `find_work_item_by_id`: Retrieves a single work item by ID.
  * `update_work_item_record`: Validates work item and new assignee existence and active status before updating fields.
  * `remove_work_item`: Deletes work item record safely with transaction rollback.

### 5. `app/main.py` — FastAPI Routing & Controllers
* **Application Entry Point:** Configures the FastAPI app instance, metadata, and auto-generates interactive Swagger UI docs at `/docs`.
* **Automatic Table Creation:** Calls `models.Base.metadata.create_all(bind=engine)` on startup to ensure database schemas exist.
* **Endpoint Routing:** RESTful endpoints for health check, employee CRUD, and work item CRUD.
* **Input Constraints:** Enforces path constraints (`id > 0`, `work_item_id > 0`) and query parameters (`limit: 1–100`, `offset >= 0`, `employee_id > 0`).

---

## Database Relationship Explanation

```mermaid
erDiagram
    EMPLOYEES ||--o{ WORK_ITEMS : "has (1 : N)"
    EMPLOYEES {
        int id PK "Auto-increment"
        string name "Required"
        string email UK "Unique"
        string department "Required"
        string primary_skill "Required"
        string location "Required"
        enum work_mode "WFH | WFO"
        boolean is_active "Default True"
        datetime created_at "Auto timestamp"
    }
    WORK_ITEMS {
        int id PK "Auto-increment"
        string title "Required, non-empty"
        text description "Optional"
        int employee_id FK "References employees.id"
        enum status "TODO | IN_PROGRESS | COMPLETED"
        enum priority "LOW | MEDIUM | HIGH"
        date due_date "Optional"
        datetime created_at "Auto timestamp"
        datetime updated_at "Auto timestamp"
    }
```

### 1. One-to-Many (`1 : N`) Connection
* One employee can be assigned multiple work items (`0, 1, or many`).
* Each work item belongs to exactly one employee via `employee_id`.

### 2. Foreign Key & SQLAlchemy Relationship
* **Database Constraint:** `work_items.employee_id` defines `ForeignKey("employees.id")`, enforcing relational integrity at the MySQL database engine level.
* **SQLAlchemy Bidirectional Mapping:**
  * On `WorkItem`: `assigned_employee = relationship("Employee", back_populates="work_items")`
  * On `Employee`: `work_items = relationship("WorkItem", back_populates="assigned_employee")`
* **Seamless Pydantic Serialization:** Because the relationship attribute on `WorkItem` is named `assigned_employee`, Pydantic's `WorkItemDetails` schema automatically resolves and nests the employee's `id`, `name`, and `email` without manual object transformation.

### 3. Referential Integrity & Deletion Protection
* When an employee has assigned work items, attempting to delete that employee via `DELETE /employees/{id}` triggers a foreign key integrity check in MySQL.
* The service catches `IntegrityError` and returns **`HTTP 409 Conflict`** with a clear message:
  > *"Cannot delete employee with ID {id} because they have related records in the database."*
* This prevents orphaned work items and ensures data consistency.

---

## Application Request Flow

```mermaid
flowchart LR
    A["Client / Swagger UI"] -->|"1. HTTP Request"| B["app/main.py"]
    B -->|"2. Validate"| C["app/schemas.py"]
    B -->|"3. Get Session"| D["app/database.py"]
    B -->|"4. Run Service"| E["app/services.py"]
    E -->|"5. Query via models.py"| F[("MySQL Database")]
    F -->|"6. Rows"| E
    E -->|"7. Formatted JSON"| B
    B -->|"8. Response (200 / 201 / 204)"| A
```

---

## Database Setup & Configuration

### 1. Create MySQL Database
Log in to MySQL:
```bash
mysql -u root -p
```
Run this command:
```sql
CREATE DATABASE IF NOT EXISTS employee_db;
EXIT;
```

### 2. Configure `.env`
Create a `.env` file in the project root:
```env
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=YOUR_MYSQL_PASSWORD
DATABASE_NAME=employee_db
```

---

## How to Run

1. **Activate Virtual Environment:**
   ```bash
   source venv/bin/activate
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Start the Server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
4. **Open Swagger Documentation:**
   Go to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to test the endpoints interactively.

---

## API Endpoints Summary

| Method | Endpoint | Description | Status Codes |
|---|---|---|---|
| `GET` | `/` | Welcome message | `200` |
| `GET` | `/health` | Database connection health check | `200`, `503` |
| `POST` | `/employees` | Add new employee | `201`, `400`, `422` |
| `GET` | `/employees` | List employees (with search, filters & pagination) | `200`, `422` |
| `GET` | `/employees/{id}` | Get employee by ID | `200`, `404`, `422` |
| `PUT` | `/employees/{id}` | Update employee details | `200`, `400`, `404`, `422` |
| `DELETE` | `/employees/{id}` | Delete employee (protected by FK constraint) | `200`, `404`, `409`, `422` |
| `POST` | `/work-items` | Create and assign a work item to an employee | `201`, `400`, `404`, `422` |
| `GET` | `/work-items` | List work items (with search, filters & pagination) | `200`, `422` |
| `GET` | `/work-items/{work_item_id}` | Get single work item by ID | `200`, `404`, `422` |
| `PUT` | `/work-items/{work_item_id}` | Update work item details or reassign employee | `200`, `400`, `404`, `422` |
| `DELETE` | `/work-items/{work_item_id}` | Delete work item | `200`, `404`, `422` |

---

## Work Item API Details & Sample Requests

### 1. Create and Assign Work Item (`POST /work-items`)
* **Status:** `201 Created`
* **Validation:** Assignee employee must exist in the database and must be active (`is_active = True`). Title must not be blank or whitespace.

#### Sample Request Body:
```json
{
  "title": "Prepare weekly status report",
  "description": "Consolidate sprint progress and blockers for leadership sync",
  "employee_id": 1,
  "status": "TODO",
  "priority": "MEDIUM",
  "due_date": "2026-10-15"
}
```

#### Sample Response (`201 Created`):
```json
{
  "id": 1,
  "title": "Prepare weekly status report",
  "description": "Consolidate sprint progress and blockers for leadership sync",
  "employee_id": 1,
  "status": "TODO",
  "priority": "MEDIUM",
  "due_date": "2026-10-15",
  "created_at": "2026-10-05T14:30:00",
  "assigned_employee": {
    "id": 1,
    "name": "Alice Smith",
    "email": "alice.smith@example.com"
  }
}
```

---

### 2. List Work Items with Filtering, Search & Pagination (`GET /work-items`)
* **Status:** `200 OK`
* **Supported Query Parameters:**
  * `search` *(string, optional)*: Partial and case-insensitive search strictly on the `title`.
  * `employee_id` *(integer, optional, `gt=0`)*: Filter by assigned employee ID.
  * `status` *(enum, optional)*: Filter by status (`TODO`, `IN_PROGRESS`, `COMPLETED`).
  * `priority` *(enum, optional)*: Filter by priority (`LOW`, `MEDIUM`, `HIGH`).
  * `limit` *(integer, default `10`, range `1–100`)*: Maximum records to return.
  * `offset` *(integer, default `0`, min `0`)*: Number of records to skip.
* **SQL Optimization:** All filtering, pre-pagination counting (`query.count()`), deterministic ascending ordering (`order_by(models.WorkItem.id.asc())`), and pagination (`offset()`, `limit()`) run directly on the database engine.

#### Sample Request:
```http
GET /work-items?status=TODO&priority=MEDIUM&limit=10&offset=0
```

#### Sample Response (`200 OK`):
```json
{
  "total": 2,
  "limit": 10,
  "offset": 0,
  "items": [
    {
      "id": 1,
      "title": "Prepare weekly status report",
      "description": "Consolidate sprint progress and blockers for leadership sync",
      "employee_id": 1,
      "status": "TODO",
      "priority": "MEDIUM",
      "due_date": "2026-10-15",
      "created_at": "2026-10-05T14:30:00",
      "assigned_employee": {
        "id": 1,
        "name": "Alice Smith",
        "email": "alice.smith@example.com"
      }
    }
  ],
  "message": "Found 2 work item(s) matching your filters."
}
```

---

### 3. Get Work Item by ID (`GET /work-items/{work_item_id}`)
* **Status:** `200 OK`
* **Error:** `404 Not Found` if the work item ID does not exist.

#### Sample Request:
```http
GET /work-items/1
```

#### Sample Response (`200 OK`):
```json
{
  "id": 1,
  "title": "Prepare weekly status report",
  "description": "Consolidate sprint progress and blockers for leadership sync",
  "employee_id": 1,
  "status": "TODO",
  "priority": "MEDIUM",
  "due_date": "2026-10-15",
  "created_at": "2026-10-05T14:30:00",
  "assigned_employee": {
    "id": 1,
    "name": "Alice Smith",
    "email": "alice.smith@example.com"
  }
}
```

---

### 4. Update Work Item or Reassign (`PUT /work-items/{work_item_id}`)
* **Status:** `200 OK`
* **Validation:** Work item must exist (otherwise `404`). If reassigning to another `employee_id`, target employee must exist (otherwise `404`) and must be active (otherwise `400`).

#### Sample Request Body:
```json
{
  "title": "Finalize weekly status report",
  "description": "Review sprint metrics and distribute report",
  "employee_id": 2,
  "status": "IN_PROGRESS",
  "priority": "HIGH",
  "due_date": "2026-10-18"
}
```

#### Sample Response (`200 OK`):
```json
{
  "id": 1,
  "title": "Finalize weekly status report",
  "description": "Review sprint metrics and distribute report",
  "employee_id": 2,
  "status": "IN_PROGRESS",
  "priority": "HIGH",
  "due_date": "2026-10-18",
  "created_at": "2026-10-05T14:30:00",
  "assigned_employee": {
    "id": 2,
    "name": "Bob Johnson",
    "email": "bob.johnson@example.com"
  }
}
```

---

### 5. Delete Work Item (`DELETE /work-items/{work_item_id}`)
* **Status:** `200 OK`
* **Behavior:** Deletes the record and returns a success confirmation message.
* **Error:** `404 Not Found` if the work item ID does not exist.

#### Sample Request:
```http
DELETE /work-items/1
```

#### Sample Response (`200 OK`):
```json
{
  "message": "Work item with ID 1 deleted successfully."
}
```

---

## Validation & Error Handling

| Scenario | HTTP Status | Error Message / Behavior |
|---|---|---|
| **Non-existent Work Item** | `404 Not Found` | `{"detail": "Work item with ID {id} not found"}` |
| **Non-existent Employee (Assign / Reassign)** | `404 Not Found` | `{"detail": "Employee with ID {employee_id} not found."}` |
| **Assigning to Inactive Employee** | `400 Bad Request` | `{"detail": "Cannot assign work item to inactive employee ID {id}."}` |
| **Deleting Employee with Active Work Items** | `409 Conflict` | `{"detail": "Cannot delete employee with ID {id} because they have related records in the database."}` |
| **Blank or Whitespace-only Title** | `422 Unprocessable Content` | `{"detail": [{"msg": "Value error, Title cannot be empty or contain only whitespace."}]}` |
| **Invalid Status or Priority Value** | `422 Unprocessable Content` | `{"detail": [{"msg": "Input should be 'TODO', 'IN_PROGRESS' or 'COMPLETED'"}]}` |
| **Due Date in the Past** | `422 Unprocessable Content` | `{"detail": [{"msg": "Value error, Due date cannot be in the past."}]}` |
| **Negative or Zero IDs (`id <= 0`)** | `422 Unprocessable Content` | Enforced by FastAPI's `Path(..., gt=0)` and Pydantic's `Field(..., gt=0)` |
| **Pagination Out of Range (`limit > 100`, `limit < 1`, `offset < 0`)** | `422 Unprocessable Content` | Enforced by FastAPI's `Query(ge=1, le=100)` and `Query(ge=0)` |
| **Database Failure / Downtime** | `500 Internal Server Error` / `503 Service Unavailable` | Graceful rollback via `db.rollback()` to keep sessions clean |

---

## Assumptions Made

1. **Foreign Key Integrity:** Deleting an employee who has assigned work items is strictly forbidden (`409 Conflict`) to prevent orphaned records in `work_items`.
2. **Active Assignees:** Work items can only be created for or reassigned to active employees (`is_active = True`).
3. **Ascending Order:** Work items are sorted deterministically in ascending order by primary key ID (`models.WorkItem.id.asc()`).
4. **Pre-Pagination Total:** The `total` field in `GET /work-items` reflects the total number of matching records before `limit` and `offset` are evaluated.
5. **Partial Title Search:** The `search` query parameter evaluates against `models.WorkItem.title` using case-insensitive SQL matching (`func.lower()` and `LIKE %...%`).
6. **Due Date Constraint:** The `due_date` field is an optional date (`YYYY-MM-DD`) that cannot be set in the past.
7. **HTTP 204 Specification:** Deletion conforms to RFC 9110 by returning `HTTP 204 No Content` with an empty response body.

---

## Difficulties Faced & Solutions

  **URL Path Naming Standards:** Initial routes used underscores (`/work_items`) which diverged from REST conventions and project specifications (`/work-items`). Corrected all endpoints to use hyphens consistently.
  **HTTP 204 Response Body Conflict:** Returning a JSON dictionary (`{"message": ...}`) alongside HTTP `204 No Content` produces warnings and violates HTTP protocol standards. Resolved by returning `Response(status_code=status.HTTP_204_NO_CONTENT)`.
  **Seamless Relationship Serialization:** Pydantic models typically require manual mapping when embedding related ORM models. By configuring the relationship name on `WorkItem` as `assigned_employee` and enabling `from_attributes=True` on `AssignedEmployee`, FastAPI automatically serializes the nested employee data cleanly.
  **Preventing Broken Transactions:** Reassigning work items to non-existent employees could result in unhandled foreign key integrity errors. Added explicit validation checks using `find_employee_by_id()` prior to executing updates, paired with `try...except IntegrityError` and `db.rollback()`.


### 1. Database Setup, Engine & Connection Issues
* **FastAPI Database Session Dependency Error:**  
  * *Difficulty:* Initially using `db: Session = get_db()` caused FastAPI to treat the database generator as a regular parameter instead of resolving it, failing to inject a database session.
  * *Solution:* Injected the session using FastAPI's dependency system: `db: Session = Depends(get_db)`.
* **MySQL 8+ Authentication (`caching_sha2_password`):**  
  * *Difficulty:* Connecting PyMySQL to MySQL 8+ resulted in `Authentication plugin 'caching_sha2_password' is not supported` errors.
  * *Solution:* Installed the `cryptography` Python package and configured the connection via `URL.create()` to support secure modern authentication.
* **Special Characters in Database Credentials:**  
  * *Difficulty:* Passwords containing special characters (like `@`, `:`, `%`) broke plain string interpolation in `DATABASE_URL`.
  * *Solution:* Used SQLAlchemy's `URL.create(drivername="mysql+pymysql", ...)` to safely encode credentials.
* **Leaking `.env` in Git Tracking:**  
  * *Difficulty:* `.gitignore` initially had `.env/` (ignoring a directory), which left the `.env` configuration file untracked and vulnerable to being committed.
  * *Solution:* Corrected the rule to `.env` to properly ignore the file.

---

### 2. Schema Validation, CRUD & Data Integrity
* **Swagger UI Missing PUT Edit Fields:**  
  * *Difficulty:* In `PUT /employees/{id}`, the request body fields were not showing up in the Swagger documentation.
  * *Solution:* Inherited `EmployeeEdit` from `EmployeeBase` so that all modifiable fields (`name`, `department`, etc.) were properly included.
* **Case-Insensitive Email Duplicate Checks:**  
  * *Difficulty:* Standard string comparisons allowed duplicate emails with different casing (e.g., `user@example.com` vs `USER@EXAMPLE.COM`).
  * *Solution:* Used SQL's `func.lower(Employee.email) == email.strip().lower()` for case-insensitive duplicate checks.
* **JSON Boolean Syntax Error in Request Payloads (RFC 8259):**  
  * *Difficulty:* Sending Python-style booleans (`"is_active": False`) produced HTTP `422 JSON decode error (Expecting value)`.
  * *Solution:* Ensured all client requests follow the JSON specification by strictly using lowercase booleans (`true` / `false`).
* **Preserving Immutable Fields on Updates:**  
  * *Difficulty:* Updating an employee risked overwriting their original `created_at` timestamp.
  * *Solution:* Explicitly updated only the mutable fields and left `created_at` intact.

---

### 3. Search, Filtering & Pagination Logic
* **Response Validation Mismatch on Pagination:**  
  * *Difficulty:* When changing `GET /employees` from a plain list to a pagination object (`{ total, limit, offset, items }`), FastAPI threw an HTTP `500 ResponseValidationError`.
  * *Solution:* Updated the route's `response_model` from `list[EmployeeDetails]` to the envelope schema `PaginatedEmployeeResponse`.
* **Pre-Pagination Count Calculation:**  
  * *Difficulty:* Calling `.count()` after applying `.limit()` and `.offset()` only counted the items on the current page instead of total database matches.
  * *Solution:* Executed `total = query.count()` *before* chaining `.offset()` and `.limit()`.
* **Query Parameter Boundary Validation:**  
  * *Difficulty:* Negative offsets or limits greater than 100 could cause unexpected database behavior or performance degradation.
  * *Solution:* Enforced boundaries using FastAPI's `Query(ge=1, le=100)` for limit and `Query(ge=0)` for offset, returning standard HTTP `422` errors for invalid inputs.

---

### 4. Relational Database & Work Item Management
* **Foreign Key Constraints & Referential Integrity:**  
  * *Difficulty:* Deleting an employee who has assigned work items caused a database crash due to foreign key constraints.
  * *Solution:* Caught `IntegrityError` in `remove_employee()` and returned a descriptive **`409 Conflict`** response (`"Cannot delete employee because they have related records"`), preventing orphaned records.
* **Nested Pydantic Serialization for Relationships:**  
  * *Difficulty:* Pydantic's `WorkItemDetails` needs to include employee information (`id`, `name`, `email`), which normally requires manual joins and mapping.
  * *Solution:* Named the SQLAlchemy relationship `assigned_employee` on `WorkItem` to match the Pydantic field name and enabled `from_attributes=True`, allowing FastAPI to automatically serialize the nested employee details.
* **REST URL Path Naming Inconsistency:**  
  * *Difficulty:* Initial endpoints used underscores (`/work_items`), which conflicted with RESTful conventions and the project specification (`/work-items`).
  * *Solution:* Standardized all routes to use hyphens (`POST /work-items`, `GET /work-items/{id}`, etc.).
* **HTTP 204 No Content Protocol Conflict:**  
  * *Difficulty:* Returning a JSON dictionary `{"message": ...}` with status `204` violated RFC 9110 (which mandates that 204 responses must not contain a message body).
  * *Solution:* Returned `Response(status_code=status.HTTP_204_NO_CONTENT)` with an empty body.
* **Reassignment Validation:**  
  * *Difficulty:* Reassigning a work item to an employee who does not exist or is inactive (`is_active = False`) could cause orphaned or corrupt task allocations.
  * *Solution:* Added pre-commit checks verifying that the target employee exists (returning `404`) and is currently active (returning `400`).