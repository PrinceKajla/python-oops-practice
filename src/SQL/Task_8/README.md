# PostgreSQL Database Integration

**Task ID:** SQL-PY-008

This is the PostgreSQL continuation of the student-management system from
SQL-PY-001 through SQL-PY-007. Python remains the application layer;
PostgreSQL stores the related student, course, and transfer-history data.

## Project files

- `main.py` provides the student/course menus and JOIN-based listings.
- `database.py` owns one PostgreSQL connection, creates the schema, and runs
  parameterized queries and course-transfer transactions.
- `student.py` and `course.py` validate the application models.
- `config.py` loads database credentials from environment variables or `.env`.
- `.env.example` documents the required settings. Keep your local `.env`
  private; it is ignored by Git.

## Setup

1. Install PostgreSQL and start its server.
2. Create the database (the application creates tables, not databases):

   ```sql
   CREATE DATABASE student_management;
   ```

3. Create a local `.env` from `.env.example`, then enter your PostgreSQL
   password in `DB_PASSWORD`.
4. From this directory, install dependencies and start the application:

   ```console
   python -m venv .venv
   .venv\Scripts\activate
   python -m pip install -r requirements.txt
   python main.py
   ```

   The application confirms the connection before displaying its menu. A
   missing/unavailable server and invalid credentials are reported without
   displaying a traceback or the password.

## Schema and behavior

`create_tables()` creates `courses`, `students`, and
`student_course_history`. Course IDs and history IDs use PostgreSQL `SERIAL`;
marks use `NUMERIC(5, 2)`; foreign keys and checks preserve the earlier
relationship and validation rules. Add courses before students. Course IDs
are generated and shown when a course is added.

All values are passed separately using psycopg's `%s` placeholders. Student
listings use an `INNER JOIN` to display the course name. A transfer locks the
student row, updates its course, inserts its history record, and commits both
changes together. Any failure rolls back both writes.

The connection is managed by `Database` and closed when the application exits.
The course-history foreign keys preserve the audit trail, so a student or
course referenced by transfer history cannot be deleted.

## Required checks

1. Add BCA, BBA, MCA, and MBA and at least five students.
2. View all students and verify the course-name JOIN and marks.
3. Update a student's name, age, or marks; verify the displayed values.
4. Delete a student without transfer history and verify it is gone.
5. Transfer a student from BCA to MCA, then view transfer history.
6. To test rollback, temporarily create a PostgreSQL trigger that raises an
   exception before inserting into `student_course_history`. Attempt a
   transfer and verify the student's original course remains and no history
   row was added. Drop the test trigger afterwards.
7. Exit, restart the application (or PostgreSQL), and verify committed rows
   remain.
8. Verify tables with `\dt` in `psql` while connected to `student_management`.

Example rollback-test trigger (run only in a test database):

```sql
CREATE FUNCTION reject_course_history() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'simulated history failure';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER fail_course_history
BEFORE INSERT ON student_course_history
FOR EACH ROW EXECUTE FUNCTION reject_course_history();

-- Remove the test objects after verifying rollback:
DROP TRIGGER fail_course_history ON student_course_history;
DROP FUNCTION reject_course_history();
```

## Practical SQL

```sql
INSERT INTO students (student_id, name, age, course_id, marks)
VALUES (101, 'Asha', 20, 1, 91.50);

UPDATE students SET marks = 95.00 WHERE student_id = 101;
DELETE FROM students WHERE student_id = 101;

SELECT s.student_id, s.name, c.course_name, s.marks
FROM students AS s
INNER JOIN courses AS c ON s.course_id = c.course_id;

SELECT student_id, name, marks
FROM students
ORDER BY marks DESC
LIMIT 3;
```

## Key concepts

- PostgreSQL is a client-server relational database; psycopg is the Python
  client driver.
- A connection identifies the server and database and carries the session;
  a cursor executes SQL and reads its result.
- Environment variables keep credentials out of source code.
- Parameterized statements separate user values from SQL syntax and prevent
  those values from changing the query.
- A foreign key enforces a valid relationship between tables.
- `VARCHAR` bounds text length, `NUMERIC` stores exact decimal values, and
  `SERIAL` supplies an integer from a sequence.
- `COMMIT` persists a transaction; `ROLLBACK` cancels its uncommitted work.
