# Student Filtering and Sorting

**Task ID:** SQL-PY-004

## Project Files

- `main.py` runs the interactive student-management application.
- `student.py` defines and validates the `Student` model.
- `database.py` manages SQLite CRUD, filtering, sorting, and top-N queries.
- `student_management.db` is created beside these files on first run.

## Run

From this folder, run:

```console
python main.py
```

The menu retains all SQL-PY-003 operations and adds course and name search, minimum-marks filtering, marks sorting, and top-N results. Course search includes exact course matching, an AND filter (course plus minimum marks), and an OR filter (either of two courses).

## Filtering and Sorting Queries

- Course: `SELECT * FROM students WHERE course = ?`
- Minimum marks: `SELECT * FROM students WHERE marks >= ?`
- Partial name: `SELECT * FROM students WHERE name LIKE ?`; Python binds `f"%{keyword}%"`.
- Course and marks (AND): `SELECT * FROM students WHERE course = ? AND marks >= ?`
- Either course (OR): `SELECT * FROM students WHERE course = ? OR course = ?`
- Highest marks first: `SELECT * FROM students ORDER BY marks DESC`
- Lowest marks first: `SELECT * FROM students ORDER BY marks ASC`
- Top N: `SELECT * FROM students ORDER BY marks DESC LIMIT ?`

All user values are parameterized. Sort direction is selected from fixed SQL fragments (`ASC` or `DESC`) rather than user-provided SQL. Marks must be between 0 and 100, course cannot be empty, and top N must be a positive integer. The parameterized `LIMIT ?` query is supported by SQLite.

## Required Behavior Checks

For a useful sample dataset, add students from at least two courses with different names and marks through the menu. Then verify:

1. Search by course `BCA` returns only BCA students.
2. Minimum marks `80` returns only students with marks at least 80.
3. Name keyword `ri` returns names containing that substring.
4. Descending and ascending sorts return marks in the requested order.
5. Top 3 returns at most three students, ordered by marks descending.
6. Minimum marks `150` reports `Invalid marks.`
7. Top N `-5` reports `Number of students must be greater than 0.`
8. Course search option 2 returns only students matching both the course and minimum marks; option 3 returns students matching either course.

## Assignment Questions

1. `WHERE` filters which rows a query returns or changes.
2. `AND` requires every condition to be true; `OR` requires at least one condition to be true.
3. `LIKE` compares text using a pattern, commonly for partial matching.
4. `%` matches any sequence of zero or more characters.
5. `ORDER BY` sorts query results by one or more columns.
6. `ASC` sorts ascending; `DESC` sorts descending.
7. `LIMIT` restricts the maximum number of returned rows.
8. Use `SELECT * FROM students ORDER BY marks DESC LIMIT 5`.
9. Use `SELECT * FROM students WHERE marks > ?` and bind `80`.
10. Use `SELECT * FROM students WHERE name LIKE ?` and bind `f"%{keyword}%"`.
11. Without `ORDER BY`, result order is not guaranteed.
12. Concatenating input can allow SQL injection or malformed queries; parameter binding keeps values separate from SQL syntax.

## Viva Questions

1. Query `WHERE marks > ?` with the value `80`.
2. Query `ORDER BY marks DESC LIMIT 1`.
3. Use `LIKE ?` with a pattern such as `f"%{keyword}%"`.
4. `ASC` sorts from low to high; `DESC` sorts from high to low.
5. `LIMIT 5` returns no more than five rows.
6. Yes. For example: `SELECT * FROM students WHERE course = ? ORDER BY marks DESC`.
