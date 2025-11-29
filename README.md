# HRMS Leave Management System

A Django-based leave management system with employee and manager portals.

## Features

- **Employee Portal**

  - View leave balance
  - Apply for leave with validation
  - View leave history

- **Manager Portal**
  - View pending leave requests
  - Approve/Reject requests via AJAX
  - Real-time updates without page reload

## Tech Stack

- Django 4.2
- MySQL
- Bootstrap 5
- Vanilla JavaScript (Fetch API)

## Setup Instructions

### Prerequisites

- Python 3.8+
- MySQL Server
- pip

### Installation

1. Clone the repository:

```bash
git clone https://github.com/antu41/Mini-HRMS-Leave-Management-System.git
cd hrms_leave_management
```

2. Create and activate virtual environment:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create MySQL database:

```sql
CREATE DATABASE hrms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

5. Update database credentials in `hrms_project/settings.py`

6. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

7. Create demo users:

```bash
python create_demo_users.py
```

8. Run development server:

```bash
python manage.py runserver
```

9. Access the application at `http://localhost:8000`

## Demo Credentials

- **Employee**: username: `employee`, password: `password123`
- **Manager**: username: `manager`, password: `password123`

## Project Structure

hrms_leave_management/
├── leave_management/ # Main app
│ ├── models.py # Database models
│ ├── views.py # View logic
│ ├── forms.py # Form definitions
│ ├── urls.py # URL routing
│ └── templates/ # HTML templates
├── hrms_project/ # Project settings
├── manage.py # Django management
└── requirements.txt # Dependencies

## Usage

### Employee Workflow

1. Login with employee credentials
2. View current leave balance on dashboard
3. Fill out leave application form
4. System validates against available balance
5. Submit request and view in history

### Manager Workflow

1. Login with manager credentials
2. View all pending requests in table
3. Click Approve/Reject buttons
4. System updates via AJAX
5. Row disappears from table without reload

## API Endpoints

- `POST /api/leave-request/<id>/process/` - Process leave request (AJAX)
