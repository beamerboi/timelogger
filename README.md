# TimeLogger - JIRA Time Tracking Application

## Academic Context
This project was developed as part of the "Programmation web avec Python" course at SESAME University for the academic year 2024/2025, class INGTA-2C.

## Project Overview
TimeLogger is a web application designed to integrate with JIRA, allowing Focus Corporation employees to efficiently track their work hours and manage their JIRA tickets. The application provides a secure and user-friendly interface for logging time and managing tasks.

## Key Features

### Authentication & Security
- Secure user registration and login system
- Email verification using Gmail SMTP
- Domain restriction to @focus-corporation.com emails
- Password strength requirements
- Session management with Flask-Login

### JIRA Integration
- View assigned tickets from current sprint
- Log work hours directly to JIRA
- Real-time ticket status synchronization
- Automated daily reminders for pending time logs

### Time Management
- Track daily and weekly work hours
- View work history and statistics
- Manage multiple JIRA tickets
- Generate time reports

## Technical Stack

### Backend
- Flask web framework
- PostgreSQL database
- SQLAlchemy ORM
- Flask extensions:
  - Flask-Login for authentication
  - Flask-Mail for email services
  - Flask-Migrate for database migrations
  - Flask-SQLAlchemy for database ORM

### Frontend
- HTML templates with Jinja2
- Tailwind CSS for styling
- JavaScript for client-side validation

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd timelogger
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables (.env):
   ```plaintext
   # Flask Configuration
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://username:password@localhost/timelogger

   # JIRA Configuration
   JIRA_SERVER=https://focus-corporation.atlassian.net
   JIRA_EMAIL=your-jira-email@focus-corporation.com
   JIRA_API_TOKEN=your-jira-api-token

   # Email Configuration
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-specific-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com

   # Flask App
   FLASK_APP=app.py
   ```

5. Initialize database:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. Run the application:
   ```bash
   flask run
   ```

## Project Structure