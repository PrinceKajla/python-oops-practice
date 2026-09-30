# Student Database with Constraints

**Task ID:** SQL-PY-002

## Project Files

- `main.py` runs the interactive student-management application.
- `student.py` defines `Student` and validates values before database access.
- `database.py` manages the SQLite connection, constrained table, inserts, and queries.
- `student_management.db` is created beside these project files when the application runs.

## Database Design

| Column | Type | Constraint |
| --- | --- | --- |
| `student_id` | INTEGER | `PRIMARY KEY` |
| `name` | TEXT | `NOT NULL` |
| `age` | INTEGER | `NOT NULL`, `CHECK (age > 0)` |
| `course` | TEXT | `NOT NULL` |
| `marks` | REAL | `NOT NULL`, `CHECK (marks >= 0 AND marks <= 100)` |

The primary key rejects duplicate student IDs. Required fields cannot be `NULL`, while the checks prevent invalid ages and marks even if a record bypasses the Python application. Python validation runs first to provide clear feedback; database constraints provide a second integrity boundary.

## Run

From this folder, run:

```console
python main.py
```

Use the menu to add, list, or search for students. A duplicate ID is reported as `Student ID already exists.` A missing search result is reported as `Student not found.`

## SQL Operations

- `CREATE TABLE IF NOT EXISTS` creates the students table with its constraints.
- `INSERT INTO` uses placeholders and commits a valid record; failed inserts are rolled back.
- `SELECT` lists student records, and `SELECT ... WHERE student_id = ?` searches by ID.

## Required Behavior Checks

1. ID 6, Karan, 20, BCA, 85 is inserted successfully.
2. Inserting ID 1 when it already exists reports `Student ID already exists.`
3. Age `-5` is rejected by Python validation; the database also rejects non-positive ages.
4. Marks `150` is rejected by Python validation; the database also rejects marks outside 0–100.
5. An empty name reports `Student name cannot be empty.`
6. An empty course reports a course validation error.
7. Searching for an existing ID displays that student's record.
8. Searching for an unknown ID reports `Student not found.`

## Key Concepts

- A primary key uniquely identifies a row and cannot be duplicated.
- `NOT NULL` prevents a missing value; an empty string is a value, not SQL `NULL`.
- `CHECK` enforces a condition when a row is written.
- Validation belongs in both Python and the database: Python gives useful application feedback, while database constraints protect stored data from every writer.
- A `DEFAULT` supplies a value when an insert omits a column. It is not needed for the required schema in this task.