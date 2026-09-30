# Python-SQL Database Foundation

**Task ID:** SQL-PY-001

## Problem

Build a University Student Management System that stores student records in SQLite so the data remains available after the program exits.

## Technologies

- Python
- SQLite through Python's built-in `sqlite3` module
- SQL

## Project Files

- `main.py` runs the interactive application.
- `student.py` defines and validates the `Student` class.
- `database.py` connects to SQLite and performs table creation, insertion, listing, and ID search.
- `student_management.db` is created in this folder the first time the program runs.

## Database

The `students` table contains `student_id` (INTEGER), `name` (TEXT), `age` (INTEGER), `course` (TEXT), and `marks` (REAL). The database file is generated at runtime and is not required to start the application.

## Run

From this folder, run:

```console
python main.py
```

Choose an option to add a student, list all students, search by ID, or exit. The SQLite connection is closed when the application exits.

## SQL Operations

- `CREATE TABLE IF NOT EXISTS` creates the table on startup when it does not already exist.
- `INSERT INTO` stores a validated student, and `commit()` persists the change.
- `SELECT` retrieves all students.
- `SELECT ... WHERE student_id = ?` searches by ID. The `?` placeholder keeps user values separate from SQL text.

## Validation and Errors

- Student ID must be an integer.
- Name and course must not be empty.
- Age must be an integer greater than zero.
- Marks must be a number from 0 through 100.
- Invalid input is reported before an INSERT is attempted. SQLite errors are reported by the application, and a missing search result displays `Student not found.`

## Test Results

The required behavior was checked with an in-memory SQLite database: a valid student can be inserted and retrieved; an unknown ID returns no record; negative age, marks above 100, and an empty name are rejected by validation.

## How Python Communicates With SQL

`sqlite3.connect()` opens the database and returns a connection. The connection executes SQL statements and returns query rows; `commit()` makes writes persistent. Python objects represent individual students in the application, while rows in the `students` table store their data persistently.

## Assignment Questions

1. A Python object is an in-memory instance with data and behavior; a database record is a stored row of values.
2. A list disappears when the program ends and is limited to one process. A database persists data and supports querying it later.
3. SQL (Structured Query Language) is used to define, query, and change data in relational databases.
4. `sqlite3.connect()` opens a connection to a SQLite database file, creating the file if necessary.
5. `cursor.execute()` runs a SQL statement with optional values; SQLite connections also provide `execute()` directly.
6. `commit()` saves a transaction's successful changes so they persist beyond the connection.
7. A Python class defines application objects and their behavior; an SQL table defines the structure for stored rows.
8. Validation rejects invalid values before they are written, protecting the stored data and providing useful feedback.