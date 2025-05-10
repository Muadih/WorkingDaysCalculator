# WorkingDaysCalculator

WorkingDaysCalculator is a web service that calculates dates based on the number of working days or returns the number of working days between given dates.

This web service provides two main endpoints:

- **/api/v1/is-working-day**  
  Checks if a given date is a working day.  
  - Takes a `date` parameter in `YYYY-MM-DD` format.  
  - Returns whether the date is a working day or not.

- **/api/v1/working-days-between**  
  Counts working days between two dates.  
  - Takes `start_date` and `end_date` parameters in `YYYY-MM-DD` format.  
  - Returns the number of working days in the range.

Additionally, the service offers endpoints to calculate:
- The end date based on a start date and a specific number of working days, or
- The start date based on an end date and a number of working days.

The service takes into account:
- Weekends (Saturday and Sunday)
- Polish national holidays (using the [holidays](https://pypi.org/project/holidays/) package)
- Custom holidays stored in the PostgreSQL database

## Table of Contents
- [API Endpoints](#api-endpoints)
  - [1. Check if a Date is a Working Day](#1-check-if-a-date-is-a-working-day)
  - [2. Count Working Days Between Two Dates](#2-count-working-days-between-two-dates)
  - [3. Get Working Days Count](#3-get-working-days-count)
  - [4. Add a Custom Holiday](#4-add-a-custom-holiday)
  - [5. List All Holidays](#5-list-all-holidays)
  - [6. Health Check](#6-health-check)
  - [7. Readiness Check](#7-readiness-check)
  - [8. Calculate End Date Based on Start Date and Working Days](#8-calculate-end-date-based-on-start-date-and-working-days)
  - [9. Calculate Start Date Based on End Date and Working Days](#9-calculate-start-date-based-on-end-date-and-working-days)
- [Swagger Documentation](#swagger-documentation)
- [Project Structure](#project-structure)
- [Create_db.sh](#createdbsh)
- [Builder Script](#builder-script)
- [.dockerignore](#dockerignore)
- [Admin Panel](#admin-panel)
- [Azure Best Practices](#azure-best-practices)
- [Running the Container](#running-the-container)

## API Endpoints

### 1. Check if a Date is a Working Day
**Endpoint:** `/api/v1/is-working-day`  
**Method:** GET  
**Query Parameter:**  
- `date` (required) — Date in format `YYYY-MM-DD`.

**Example Request:**
```bash
curl "http://localhost:5000/api/v1/is-working-day?date=2025-05-10"
```

**Example Response:**
```json
{
  "date": "2025-05-10",
  "is_working_day": true
}
```

---

### 2. Count Working Days Between Two Dates
**Endpoint:** `/api/v1/working-days-between`  
**Method:** GET  
**Query Parameters:**  
- `start_date` (required) — Start date in format `YYYY-MM-DD`.  
- `end_date` (required) — End date in format `YYYY-MM-DD`.

**Example Request:**
```bash
curl "http://localhost:5000/api/v1/working-days-between?start_date=2025-05-01&end_date=2025-05-31"
```

**Example Response:**
```json
{
  "start_date": "2025-05-01",
  "end_date": "2025-05-31",
  "working_days": 21
}
```

---

### 3. Get Working Days Count
**Endpoint:** `/api/v1/working-days-count`  
**Method:** GET  
**Query Parameters:**  
- `start_date` (required) — Start date in format `YYYY-MM-DD`.  
- `end_date` (required) — End date in format `YYYY-MM-DD`.

**Example Request:**
```bash
curl "http://localhost:5000/api/v1/working-days-count?start_date=2025-05-01&end_date=2025-05-31"
```

**Example Response:**
```json
{
  "start_date": "2025-05-01",
  "end_date": "2025-05-31",
  "working_days_count": 21,
  "total_days": 31
}
```

---

### 4. Add a Custom Holiday
**Endpoint:** `/api/v1/holidays`  
**Method:** POST  
**Payload:** JSON with properties:
- `date` (required) — Holiday date in format `YYYY-MM-DD`.  
- `name` (required) — Name of the holiday.

**Example Request:**
```bash
curl -X POST "http://localhost:5000/api/v1/holidays" \
  -H "Content-Type: application/json" \
  -d '{"date": "2025-12-24", "name": "Christmas Eve"}'
```

**Example Response:**
```json
{
  "message": "Holiday added successfully",
  "date": "2025-12-24",
  "name": "Christmas Eve"
}
```

---

### 5. List All Holidays
**Endpoint:** `/api/v1/holidays`  
**Method:** GET

**Example Request:**
```bash
curl "http://localhost:5000/api/v1/holidays"
```

**Example Response:**
```json
[
  {
    "date": "2025-12-24",
    "name": "Christmas Eve",
    "type": "CUSTOM"
  },
  {
    "date": "2025-01-01",
    "name": "New Year's Day",
    "type": "NATIONAL"
  }
]
```

---

### 6. Health Check
**Endpoint:** `/api/v1/health`  
**Method:** GET

**Example Request:**
```bash
curl "http://localhost:5000/api/v1/health"
```

**Example Response:**
```json
{
  "status": "alive"
}
```

---

### 7. Readiness Check
**Endpoint:** `/api/v1/ready`  
**Method:** GET

**Example Request:**
```bash
curl "http://localhost:5000/api/v1/ready"
```

**Example Response (if all checks pass):**
```json
{
  "status": "ready",
  "checks": {
    "database": true,
    "holidays_service": true,
    "overall": true
  }
}
```

---

### 8. Calculate End Date Based on Start Date and Working Days
**Endpoint:** `/api/v1/calc-end-date`  
**Method:** GET  
**Query Parameters:**  
- `start_date` (required) — Start date in format `YYYY-MM-DD`.  
- `working_days` (required) — Number of working days (integer).

**Example Request:**
```bash
curl "http://localhost:5000/api/v1/calc-end-date?start_date=2025-05-01&working_days=10"
```

**Example Response:**
```json
{
  "start_date": "2025-05-01",
  "working_days": 10,
  "end_date": "2025-05-15"
}
```

---

### 9. Calculate Start Date Based on End Date and Working Days
**Endpoint:** `/api/v1/calc-start-date`  
**Method:** GET  
**Query Parameters:**  
- `end_date` (required) — End date in format `YYYY-MM-DD`.  
- `working_days` (required) — Number of working days (integer).

**Example Request:**
```bash
curl "http://localhost:5000/api/v1/calc-start-date?end_date=2025-05-15&working_days=10"
```

**Example Response:**
```json
{
  "end_date": "2025-05-15",
  "working_days": 10,
  "start_date": "2025-05-01"
}
```

---

## Swagger Documentation
The API documentation is automatically generated using Swagger (Flasgger) and is available at:
```
http://localhost:5000/api/v1/swagger
```
Open this URL in your browser to explore and interact with all the available API endpoints.

---

## Project Structure
A typical project structure for WorkingDaysCalculator might look like this:

```
WorkingDaysCalculator/
├── admin.py                 # Admin panel configuration and views
├── create_db.sh             # Script for creating the PostgreSQL database
├── Dockerfile               # Dockerfile for containerizing the application
├── .dockerignore            # Files and directories to ignore during Docker build
├── models.py                # Database models (e.g., Holiday)
├── README.md                # This documentation file
├── requirements.txt         # Project dependencies
├── wdc_service.py           # Main Flask application containing API endpoints
└── templates/               # HTML templates (if any) for the admin panel
```

This structure organizes code by functionality and helps developers quickly navigate and understand the project components.

---

## Create_db.sh
The `create_db.sh` script automates several tasks for setting up your PostgreSQL database. It will:
- Check if PostgreSQL is installed (and install it if necessary).
- Create a new database user.
- Create the database.
- Grant necessary privileges.
- Update the database URL in your `models.py` file.

**Usage:**
1. Make the script executable:
   ```bash
   chmod +x create_db.sh
   ```
2. Run the script:
   ```bash
   ./create_db.sh
   ```

*Make sure to replace* `your_secure_password` *with a secure password and run the script with appropriate permissions. Always keep your database credentials secure.*

---

## Builder Script

The `builder.sh` script automates the process of committing all changes in the local Git repository and building the Docker image. It performs the following steps:
1. Checks if there are any changes to commit.
2. If changes are found, it commits them with the message "Automated commit: commit all changes before building Docker image" and pushes them to the repository.
3. It then builds the Docker image tagged as `workingdayscalculator:latest`.

**Usage:**
```bash
chmod +x builder.sh
./builder.sh
```

> **Note:** Before deploying to Azure, remember to run your `azure_development-get_best_practices` tool if available.

---

## .dockerignore
To exclude unnecessary files from the Docker build context, add the `builder.sh` script (along with other files such as the Dockerfile and README.md) to your `.dockerignore` file.

Example `.dockerignore`:
```bash
# filepath: 
Dockerfile


.git
__pycache__
*.pyc
.env
tests/
```

---

## Admin Panel
The admin panel allows you to manage holidays in the system through a web-based interface.

**Features:**
- List all holidays with sorting and filtering.
- Add new holidays with date validation.
- Edit existing holidays.
- Delete holidays.
- Search holidays by name.
- Filter holidays by date and type.
- Responsive design with Polish language labels and Bootstrap-based styling.

**Usage:**
1. Install the necessary dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python wdc_service.py
   ```
3. Open your browser and navigate to:
   ```
   http://localhost:5000/admin
   ```

All changes made in the admin panel are automatically saved to your PostgreSQL database.

---

## Azure Best Practices
Before deploying this containerized application to Azure, please run the `azure_development-get_best_practices` tool (if available) to ensure your configuration meets Azure's guidelines. For example, if you're using Azure Container Registry (ACR), build and push your image with the following command:

```bash
az acr build --registry <your_acr_name> --image workingdayscalculator:latest .
```

Replace `<your_acr_name>` with your actual Azure Container Registry name.

---

## Running the Container

Once you have built the Docker image (either by manually running `docker build -t workingdayscalculator:latest .` or using the provided `builder.sh` script), you can run the container with the following command:

```bash
docker run -p 5000:5000 workingdayscalculator:latest
```

This command maps port 5000 on the container to port 5000 on your host machine, allowing you to access the application at:

```
http://localhost:5000
```

> **Azure Best Practices:**  
> If deploying to Azure, run the `azure_development-get_best_practices` tool (if available) to ensure your container configuration and deployment meet Azure guidelines.