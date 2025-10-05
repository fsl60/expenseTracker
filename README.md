A simple Expense Tracker web application built using Flask and SQLite that allows users to manage their daily expenses, view summaries, and categorize spending.


**Assumptions**

Each user manages their own expense records.
Categories are predefined (can be added manually in the database).
SQLite is used for local development (no external DB required).
App is designed for local or single-user use (can be extended for multi-user).
Currency is assumed to be INR (₹).

**Design Overview**

Architecture:
Frontend: HTML + CSS (Templates folder)
Backend: Flask (Python)
Database: SQLite (expenses.db)

Main Components:
app.py → Flask routes, DB connection, CRUD logic
templates/ → HTML pages (index.html, add_expense.html, update_expense.html, etc.)
static/ → CSS styles (styles.css)
expenses.db → Stores categories and expense records

Database Schema:
categories(id, name)
expenses(id, amount, category_id, description, date)

## Features
- Add, update, view, and delete expenses
- Manage categories 
- View summary and reports

##  Setup
```bash
git clone https://github.com/<your-username>/expense-tracker.git
cd expense-tracker
install falsk and werkzeug
python app.py
