# Student CRUD Operations

**Task ID:** SQL-PY-003

## Project Files

- `main.py` runs the interactive student-management application.
- `student.py` defines `Student` and validates values before database access.
- `database.py` manages the SQLite connection and CRUD operations.
- `student_management.db` is created beside these files the first time the application runs.

## Database Design

| Column | Type | Constraint |
| --- | --- | --- |
| `student_id` | INTEGER | `PRIMARY KEY` |
| `name` | TEXT | `NOT NULL` |
| `age` | INTEGER | `NOT NULL`, `CHECK (age > 0)` |
| `course` | TEXT | `NOT NULL` |
| `marks` | REAL | `NOT NULL`, `CHECK (marks >= 0 AND marks <= 100)` |

## Run

From this folder, run:

```console
python main.py
```

The menu supports adding, listing, searching, updating, and deleting students. Update and delete report whether a matching row was affected. Deletion displays the record and proceeds only when the response is `yes` (case-insensitive).

## CRUD Queries

- Create: `INSERT INTO students (student_id, name, age, course, marks) VALUES (?, ?, ?, ?, ?)`
- Read all: `SELECT * FROM students`
- Search: `SELECT * FROM students WHERE student_id = ?`
- Update: `UPDATE students SET name = ?, age = ?, course = ?, marks = ? WHERE student_id = ?`
- Delete: `DELETE FROM students WHERE student_id = ?`

Every user-provided value is bound through a `?` placeholder. The update deliberately does not change the primary key. Update values are validated with the same `Student` rules as inserts before SQL is executed. Database failures roll back the active transaction. `cursor.rowcount` is returned by update and delete methods: zero means no row matched; one means a row was changed.

## Required Behavior Checks

The app does not add sample rows automatically. To run the assignment checks from a clean database, first add ID 3, Amit, age 20, BBA, marks 76 through the menu. Then:

1. Add ID 6, Karan, 20, BCA, 85; view all and verify ID 6 appears.
2. Search ID 3 and verify Amit, 20, BBA, 76.
3. Update ID 3's marks to 90 and verify the changed record.
4. Attempt to update ID 3 with marks 150. Validation rejects it before SQL, and the record remains unchanged.
5. Delete ID 6 and confirm with `yes`; search ID 6 to verify it is gone.
6. Delete ID 100; the app reports `Student not found.`
7. Start deleting an existing record and answer `no`; the app reports `Deletion cancelled.` and the record remains.

## Assignment Questions

1. CRUD stands for Create, Read, Update, and Delete.
2. `UPDATE` changes one or more column values in existing rows.
3. `DELETE` removes matching rows from a table.
4. `WHERE` limits an update to the intended row or rows.
5. Without `WHERE`, an update can change every row in the table.
6. Without `WHERE`, a delete can remove every row in the table.
7. `student_id` identifies the record and is its primary key; changing it can break references and make identity harder to track.
8. `cursor.rowcount` reports how many rows a statement affected.
9. Validation during update prevents invalid values from entering the database and keeps update behavior consistent with insert behavior.
10. Confirmation helps prevent accidental or unintended deletion.

## Viva Questions

1. CRUD means Create, Read, Update, and Delete.
2. `INSERT` adds a new row; `UPDATE` modifies values in an existing row.
3. `DELETE` removes rows while leaving the table structure; `DROP` removes the table itself.
4. `WHERE` scopes a change or search to rows matching a condition.
5. An `UPDATE` or `DELETE` without `WHERE` can affect every row.
6. A primary key uniquely identifies each row in a table.
7. A primary key is used as a stable identifier and may be referenced by other data.
8. `rowcount` is the number of rows affected by an SQL statement.
9. Parameterized SQL separates values from SQL syntax, preventing user input from being interpreted as part of the query.
10. `?` is SQLite's parameter placeholder; values passed separately are bound safely by the database driver.
11. `commit()` saves the transaction's changes.
12. `rollback()` cancels uncommitted changes in the current transaction.
13. Rollback ensures a failed database operation does not leave partial changes pending.
14. Validation prevents invalid data from being written and gives users useful feedback before the operation.
15. Confirmation reduces accidental deletion of a valid record.
