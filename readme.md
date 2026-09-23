# Employee Management API

A REST API to manage employee records built using **FastAPI**, **SQLAlchemy**, and **MySQL**. Data is permanently stored in a database and persists across server restarts.

## Technologies Used

- **Language:** Python 3.12
- **Framework:** FastAPI
- **Database:** MySQL 8+
- **ORM:** SQLAlchemy 2.0
- **Driver:** PyMySQL & Cryptography
- **Validation:** Pydantic v2
- **Server:** Uvicorn


## Project Structure

```text
FastAPI-EmpManagement/
├── app/
│   ├── __init__.py
│   ├── database.py       # Engine, session, and get_db dependency
│   ├── models.py         # SQLAlchemy Employee table model
│   ├── schemas.py        # Pydantic schemas for request/response validation
│   ├── services.py       # Database CRUD operations
│   └── main.py           # FastAPI routes
├── screenshots/          # Swagger UI test screenshots
├── .env.example          # Environment template
├── .gitignore
├── requirements.txt
└── README.md
```

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

## How SQLAlchemy Connects to MySQL

- **Connection URL:** Uses the format `mysql+pymysql://<user>:<password>@<host>:<port>/<db_name>`.
- **Engine & Session:** `create_engine` creates the connection, and `sessionmaker` generates sessions.
- **Session Lifecycle (`get_db`):** Uses a generator (`yield`) as a FastAPI dependency. A session is created for each request and safely closed in a `finally` block.
- **Auto Table Creation:** `models.Base.metadata.create_all(bind=engine)` creates the `employees` table automatically when the app starts.

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
   uvicorn app.main:app --reload --port 8001
   ```
4. **Open Swagger Documentation:**
   Go to [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs) to test the endpoints.

---

## API Endpoints

| Method | Endpoint | Description | Status Codes |
|---|---|---|---|
| `GET` | `/` | Welcome message | `200` |
| `GET` | `/health` | Health check | `200` |
| `POST` | `/employees` | Add new employee | `201`, `400`, `422` |
| `GET` | `/employees` | List employees (with search, filters & pagination) | `200`, `422` |
| `GET` | `/employees/{id}` | Get employee by ID | `200`, `404`, `422` |
| `PUT` | `/employees/{id}` | Update employee details | `200`, `400`, `404`, `422` |
| `DELETE` | `/employees/{id}` | Delete employee | `200`, `404`, `422` |

---

## Search, Filtering & Pagination (`GET /employees`)

The `GET /employees` endpoint supports optional query parameters for search, filtering, and pagination directly at the database query level using SQLAlchemy.

### Query Parameters

| Parameter | Type | Default | Constraints | Description |
|---|---|---|---|---|
| `search` | `string` | `None` | Optional | Partial, case-insensitive search by employee name |
| `department` | `string` | `None` | Optional | Filter by department name |
| `work_mode` | `string` | `None` | `WFH`, `WFO` | Filter by work mode (validated against enum) |
| `is_active` | `boolean` | `None` | `true`, `false` | Filter by active status |
| `limit` | `integer` | `10` | `1` to `100` | Maximum number of records to return |
| `offset` | `integer` | `0` | `>= 0` | Number of records to skip (must not be negative) |

* **Combined Filtering:** All filters can be used independently or combined together.
* **Deterministic Ordering:** Results are always returned in ascending order of `id`.
* **Database-Level Execution:** Queries use SQLAlchemy `.filter()`, `.limit()`, and `.offset()` so records are filtered and paged directly in MySQL without loading entire tables into Python memory.
* **Empty Results Handling:** Returns `200 OK` with `total: 0` , `items: []` and `message: "No matches found."` if nothing matches, or an empty `items` list with the true `total` if `offset` exceeds total matching records.
* **Input Validation:** Rejects invalid values (e.g., `limit=0`, `offset=-1`, or unsupported `work_mode=HYBRID`) with a clear HTTP `422 Unprocessable Entity` response.

### Example Request

```http
GET /employees?department=Engineering&work_mode=WFH&limit=5&offset=0
```

### Example Response (`200 OK`)

```json
{
  "total": 14,
  "limit": 5,
  "offset": 0,
  "items": [
    {
      "id": 1,
      "name": "Alice Smith",
      "email": "alice.smith@example.com",
      "department": "Engineering",
      "primary_skill": "Python",
      "location": "Bangalore",
      "work_mode": "WFH",
      "is_active": true,
      "created_at": "2026-09-21T10:00:00"
    }
  ],
  "message": "Employee details fetched successfully."
}
```

---

## Key Learnings

- **Database Sessions:** How to use FastAPI's `Depends(get_db)` to provide a database session per request and ensure it always closes.
- **Transaction Rollback:** Wrapping database operations in `try-except` blocks and using `db.rollback()` on error to keep the session healthy.
- **Pydantic v2 ORM Mode:** Using `model_config = ConfigDict(from_attributes=True)` so Pydantic can read data directly from SQLAlchemy objects.
- **Separation of Concerns:** Keeping database tables in `models.py` separate from API request/response schemas in `schemas.py` and business/query logic in `services.py`.
- **Query Parameter Validation:** Leveraging FastAPI's `Query(..., ge=..., le=...)` and Enum type annotations to enforce bounds (`limit: 1-100`, `offset >= 0`) and automatic `422` error responses.
- **Efficient SQL Pagination:** Utilizing `.count()`, `.order_by()`, `.offset()`, and `.limit()` in SQLAlchemy to perform pagination efficiently on the database server.
- **Case-Insensitive Searching:** Using `func.lower()` combined with SQL `like()` for reliable case-insensitive partial substring searches across SQL databases.

---

## Difficulties Faced

- **FastAPI Dependency Error:** Using `db: Session = get_db()` caused an error because FastAPI treated it as a regular field. Resolved by using `db: Session = Depends(get_db)`.
- **PUT Request Schema in Swagger:** Initially, the PUT API did not show fields to edit in Swagger UI. Fixed by making `EmployeeEdit` inherit from `EmployeeBase`.
- **Response Validation Mismatch on Pagination:** Changing the return value of `GET /employees` from a list to a dictionary `{total, limit, offset, items}` initially caused an HTTP 500 `ResponseValidationError` because `response_model` was still `list[schemas.EmployeeDetails]`. Resolved by updating `response_model` to `schemas.PaginatedEmployeeResponse`.
- **Case-Insensitive Email Check:** Used `func.lower(Employee.email) == email.lower()` to ensure emails like `TEST@EMAIL.COM` and `test@email.com` are treated as duplicates.
- **Preserving `created_at`:** Handled updates so that `created_at` remains unchanged when an employee's details are edited.
- **Git Ignore Fix:** Fixed `.gitignore` from `.env/` to `.env` so the configuration file is properly ignored by Git.
- **JSON Boolean Syntax Error in Request Body:** When testing `PUT /employees/{id}` to update `is_active`, sending a Python-style capitalized boolean (`"is_active": False`) caused an HTTP `422 Unprocessable Content` with a `JSON decode error (Expecting value)`. According to the JSON specification (RFC 8259), booleans must strictly be lowercase (`false` or `true`), unlike Python. Resolved by ensuring all JSON payloads use lowercase boolean values.
- **MySQL Authentication & Permission Errors:** Encountered access issues connecting to the database (`Access denied for user 'root'@'localhost'` or missing `caching_sha2_password` plugin). Resolved by installing the `cryptography` package (required for MySQL 8 default authentication) and verifying database credentials in the `.env` file.

---

## Assumptions Made

- Database tables are created on startup without migration tools like Alembic.
- Email uniqueness is case-insensitive.
- New employees are active (`is_active = True`) by default.
- Results are always sorted in ascending order of employee ID.
- Name search is case-insensitive and supports partial matches.
- Default pagination returns 10 records starting from offset 0 (allowed limit: 1–100, offset >= 0).
- If no records match or offset exceeds total, an empty list is returned with HTTP 200.
- All filtering, searching, and pagination are handled directly at the (SQL) database level.