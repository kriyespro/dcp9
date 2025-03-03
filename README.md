# Dream Project Management System

A modern project management system built with Flask, TailwindCSS, and AlpineJS that helps track Dreams, Milestones, Goals, and Tasks.

## Features

- Dream Management
- Milestone Tracking
- Goal Setting
- Task Management
- User Management & Authentication
- Modern UI with TailwindCSS
- Interactive UX with AlpineJS
- Responsive Dashboard
- Role-based Access Control

## Tech Stack

- Backend: Flask 3.0.2
- Database: SQLite (Development) / PostgreSQL (Production)
- Frontend: TailwindCSS + AlpineJS
- Authentication: Flask-Login
- ORM: SQLAlchemy

## Setup Instructions

1. Create a virtual environment:
```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
flask db upgrade
flask init-db  # Creates initial admin user and test data
```

5. Run the development server:
```bash
flask run
```

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── views/
│   ├── templates/
│   │   └── components/
│   ├── static/
│   └── utils/
├── migrations/
├── tests/
├── config.py
├── requirements.txt
└── README.md
```

## Default Admin Credentials

Check `test_users.txt` for login credentials of test users including admin.

## License

MIT License # dcp9
