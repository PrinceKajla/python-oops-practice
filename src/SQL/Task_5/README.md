# Student Performance Analytics

**Task ID:** SQL-PY-005

## Project Files

- `main.py` runs the student-management and analytics menus.
- `student.py` defines and validates the `Student` model.
- `database.py` contains the CRUD, filtering, sorting, and SQL aggregation methods.
- `student_management.db` is created beside these files on first run.

## Run

From this folder, run:

```console
python main.py
```

Options 1-10 retain the SQL-PY-004 student operations. Option 11 displays student totals and marks statistics; option 12 displays course-wise statistics and courses whose average is at least 80; option 13 exits.

## Analytics Queries

- Total students: `SELECT COUNT(*) FROM students`
- Total marks: `SELECT COALESCE(SUM(marks), 0) FROM students`
- Average/highest/lowest marks: `AVG(marks)`, `MAX(marks)`, and `MIN(marks)` in SQL.
- Course report: `SELECT course, COUNT(*), AVG(marks), MAX(marks), MIN(marks) FROM students GROUP BY course`
- Course averages: `SELECT course, AVG(marks) FROM students GROUP BY course`
- Filter rows before grouping: `SELECT course, AVG(marks) FROM students WHERE marks >= ? GROUP BY course`
- HAVING filter: `SELECT course, AVG(marks) AS average_marks FROM students GROUP BY course HAVING AVG(marks) >= ?`

Aggregations run in SQLite; Python only formats the returned scalar values and grouped rows. All previous Task 4 database methods are retained. `get_total_marks()` returns zero for an empty table via SQL `COALESCE`; average, highest, and lowest marks are `None` for an empty table and display as `N/A`. Empty course reports are handled without an error.

## Required Behavior Checks

Add at least three BCA and two BBA students with different marks. Check that:

1. The total student count matches the inserted record count.
2. Total and average marks match manual calculations.
3. Highest and lowest marks match the inserted values.
4. Course statistics return the correct count, average, maximum, and minimum for each course.
5. `get_courses_above_average(80)` returns only courses with an average of 80 or more.
6. On an empty database, total students is 0, total marks is 0, undefined marks statistics display as `N/A`, and course statistics show no data without crashing.

## Assignment Questions

1. An aggregate function calculates a value from multiple rows.
2. `COUNT()` counts rows or non-NULL values.
3. `SUM()` adds numeric values.
4. `AVG()` calculates the arithmetic mean of numeric values.
5. `MIN()` returns the smallest value.
6. `MAX()` returns the largest value.
7. `GROUP BY` forms groups of rows that share a column value.
8. It lets aggregate functions calculate a result separately for each group, such as each course.
9. `WHERE` filters rows before grouping; `HAVING` filters groups after aggregation.
10. Yes. `WHERE` can filter input rows before `GROUP BY` aggregates them.
11. SQLite permits `HAVING` without `GROUP BY`, but it is usually clearer to use `WHERE` when filtering individual rows and `HAVING` for aggregate conditions.
12. Database-side aggregation avoids loading all records into Python and is more efficient for large datasets.
13. `AVG()` returns `NULL` when there are no non-NULL values; this app displays that as `N/A`.
14. An alias gives a query result column a readable temporary name.
15. One grouped query computes count, average, maximum, and minimum together, reducing duplicate queries and round trips.

## Viva Questions

1. `SELECT COUNT(*) FROM students`.
2. `SELECT AVG(marks) FROM students`.
3. `SELECT MAX(marks) FROM students`.
4. `SELECT course, COUNT(*) FROM students GROUP BY course`.
5. `WHERE` filters rows before aggregation; `HAVING` filters groups after aggregation.
6. `GROUP BY` calculates aggregates separately for each value/group.
7. `SELECT course, AVG(marks) FROM students GROUP BY course HAVING AVG(marks) > ?`, binding `80`.
