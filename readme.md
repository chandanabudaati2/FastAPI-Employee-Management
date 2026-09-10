# Employee Management API

Hi! This is my first backend project using **FastAPI** and **Python 3.12**. 

It is a REST API to manage employee details (Create, Read, Update, Delete). 
All data is stored temporarily in a Python list in memory, so no database setup is required.

--- 

## Technologies Used

- **Language:** Python 3.12
- **Framework:** FastAPI
- **Data Validation:** Pydantic v2
- **Server:** Uvicorn
- **Documentation:** Swagger UI (built-in at `/docs`)
- **Editor:** Visual Studio Code

---

## Project Structure

```text
FastAPI-nodb/
├── app/
│   ├── __init__.py       # Makes 'app' a Python package
│   ├── main.py           # Contains API routes and FastAPI app
│   ├── models.py        # Pydantic models for request & response validation
│   └── services.py       # In-memory data store and business logic
├── screenshots/          # Folder containing Swagger UI test screenshots
├── requirements.txt      # Project dependencies
├── .gitignore            # Files ignored by Git
└── README.md             # Project documentation
```

---

## Data Models & Schemas

The schemas are defined using Pydantic in `app/models.py`:

- **`WorkMode` (Enum):**
  - `"WFH"` (Work From Home)
  - `"WFO"` (Work From Office)

- **`EmployeeInput` (for creating employees):**
  - `name`: string (minimum 1 character)
  - `email`: valid corporate email string
  - `department`: string
  - `primary_skill`: string
  - `location`: string
  - `work_mode`: `"WFH"` or `"WFO"`

- **`EmployeeEdit` (for updating employees):**
  - Same fields as `EmployeeInput` plus:
  - `is_active`: boolean (defaults to `True`)

- **`EmployeeDetails` (API response model):**
  - All employee fields plus:
  - `id`: unique integer auto-generated starting from 1
  - `created_at`: datetime timestamp

---

## How to Run the Project

### 1. Create a virtual environment
```bash
python3 -m venv venv
```

### 2. Activate the virtual environment
- **On macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```
- **On Windows:**
  ```bash
  venv\Scripts\activate
  ```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the server
```bash
uvicorn app.main:app --reload --port 8001
```
The application will be running at: `http://127.0.0.1:8001`

### 5. Interactive API Documentation
Open your browser and navigate to:
- **Swagger UI:** [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)

You can test all endpoints directly using the **"Try it out"** button in Swagger UI.

---

## API Endpoints

| HTTP Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `GET` | `/` | Home / Welcome message with quick links | `200 OK` |
| `GET` | `/health` | Check if the server is running | `200 OK` |
| `POST` | `/employees` | Create a new employee | `201 Created` |
| `GET` | `/employees` | Get list of all employees | `200 OK` |
| `GET` | `/employees/{id}` | Get details of a single employee by ID | `200 OK` / `404 Not Found` |
| `PUT` | `/employees/{id}` | Update an existing employee's details | `200 OK` / `400 Bad Request` / `404 Not Found` |
| `DELETE` | `/employees/{id}` | Delete an employee by ID | `200 OK` / `404 Not Found` |

---

## Example Payloads

### 1. Create Employee (`POST /employees`)

**Request Body:**
```json
{
  "name": "Username",
  "email": "user1@example.com",
  "department": "Engineering",
  "primary_skill": "Python",
  "location": "Bangalore",
  "work_mode": "WFH"
}
```

**Response (`201 Created`):**
```json
{
  "id": 1,
  "name": "Username",
  "email": "user1@example.com",
  "department": "Engineering",
  "primary_skill": "Python",
  "location": "Bangalore",
  "work_mode": "WFH",
  "is_active": true,
  "created_at": "2026-09-10T14:00:00.000000"
}
```

### 2. Update Employee (`PUT /employees/1`)

**Request Body:**
```json
{
  "name": "Alex",
  "email": "user1@example.com",
  "department": "Cloud Platforms",
  "primary_skill": "FastAPI",
  "location": "Hyderabad",
  "work_mode": "WFO",
  "is_active": true
}
```

---

## Key Learnings

- Learn and Understanding how APIs work and testing endpoints using Swagger UI (`/docs`).
- Using HTTP methods: `GET` (view), `POST` (add), `PUT` (update), and `DELETE` (remove).
- Validating inputs (like email format and required fields) using Pydantic.
- Using proper status codes like `200`, `201`, `400`, and `404`.
- Managing and storing data using Python lists and dictionaries.

---

## Difficulties Faced

- Understanding when to use URL path (like `/employees/1`) vs. JSON body.
- Keeping `id` and `created_at` safe from being overwritten during updates.
- Understanding `422` error when input data did not match the model datatypes.
- Fixing the `Address already in use` error when restarting Uvicorn.

---

## Assumptions Made

- Data is stored in memory, so it resets when the server restarts.(NO Database)
- No two employees can have the same email.
- Employee IDs start from 1 and increase sequentially.(auto increment)
- Work mode can only be `"WFH"` or `"WFO"`.
- Newly created employees are active (`is_active = True`) by default.
