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
| `GET` | `/employees` | List all employees | `200` |
| `GET` | `/employees/{id}` | Get employee by ID | `200`, `404` |
| `PUT` | `/employees/{id}` | Update employee details | `200`, `400`, `404` |
| `DELETE` | `/employees/{id}` | Delete employee | `200`, `404` |

---

## Key Learnings

- **Database Sessions:** How to use FastAPI's `Depends(get_db)` to provide a database session per request and ensure it always closes.
- **Transaction Rollback:** Wrapping database operations in `try-except` blocks and using `db.rollback()` on error to keep the session healthy.
- **Pydantic v2 ORM Mode:** Using `model_config = ConfigDict(from_attributes=True)` so Pydantic can read data directly from SQLAlchemy objects.
- **Separation of Concerns:** Keeping database tables in `models.py` separate from API request/response schemas in `schemas.py`.

---

## Difficulties Faced

- **FastAPI Dependency Error:** Using `db: Session = get_db()` caused an error because FastAPI treated it as a regular field. Resolved by using `db: Session = Depends(get_db)`.
- **PUT Request Schema in Swagger:** Initially, the PUT API did not show fields to edit in Swagger UI. Fixed by making `EmployeeEdit` inherit from `EmployeeBase`.
```bash
FastAPIError: Invalid args for response field! Hint: check that Session is a valid Pydantic field type.
```
- **Case-Insensitive Email Check:** Used `func.lower(Employee.email) == email.lower()` to ensure emails like `TEST@EMAIL.COM` and `test@email.com` are treated as duplicates.
- **Preserving `created_at`:** Handled updates so that `created_at` remains unchanged when an employee's details are edited.
- **Git Ignore Fix:** Fixed `.gitignore` from `.env/` to `.env` so the configuration file is properly ignored by Git.
- **MySQL Authentication & Permission Errors:** Encountered access issues connecting to the database (`Access denied for user 'root'@'localhost'` or missing `caching_sha2_password` plugin). Resolved by installing the `cryptography` package (required for MySQL 8 default authentication) and verifying database credentials in the `.env` file.

---

## Assumptions Made

- Database tables are created on startup without migration tools like Alembic.
- Email uniqueness is case-insensitive.
- New employees are active (`is_active = True`) by default.
- MySQL 8 default authentication is supported via the `cryptography` package.
```