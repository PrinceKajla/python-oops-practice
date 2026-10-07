# Student Database Relationships and JOINs

**Task ID:** SQL-PY-006

## Project Files

- `main.py` runs the 15-option student and course application.
- `database.py` creates and queries the related SQLite tables.
- `student.py` models students using `course_id`.
- `course.py` models and validates courses.
- `student_management.db` is created beside these files on first run.

## Run

From this folder, run:

```console
python main.py
```

Create courses before adding students. The sample courses are BCA (ID 1), BBA (ID 2), MCA (ID 3), and MBA (ID 4). The app rejects an unknown course ID with `Invalid course ID.` Foreign-key enforcement is enabled on each SQLite connection. A course referenced by students cannot be deleted until those students are removed or reassigned.

## Database Relationships

`courses.course_id` is the primary key. `students.course_id` is a non-null foreign key referencing it. One course can relate to many students; every student must refer to an existing course. The `UNIQUE` constraint prevents duplicate course names.

- Student/course listing uses `INNER JOIN` and aliases `s` and `c`.
- Course statistics use `LEFT JOIN`, preserving courses with no students; `COUNT(s.student_id)` correctly reports zero for them.
- Courses without students use `LEFT JOIN ... WHERE s.student_id IS NULL`.
- Course filtering joins on `course_id` and filters with `c.course_name = ?`.
- Student CRUD, filtering, sorting, top-N, and SQL-side analytics from prior tasks are retained with the normalized schema.

## Required Behavior Checks

1. Add BCA, BBA, MCA, and MBA.
2. Add Rahul and Priya to BCA, Amit and Rohit to BBA, and Neha to BCA.
3. Attempt to add a student with course ID 99; verify `Invalid course ID.` and no row is inserted.
4. View students and verify each displayed row includes the course name from an `INNER JOIN`.
5. View course statistics and verify MCA and MBA have a count of zero and `N/A` for undefined marks values.
6. View courses without students and verify MCA and MBA appear.
7. Verify course statistics include student count, average, highest, and lowest marks.
8. Try deleting a course with students and verify referential integrity prevents deletion.

## Assignment Questions

1. A foreign key references a key in another table and enforces a valid relationship.
2. A primary key uniquely identifies a row in its table.
3. A relationship connects records in different tables through related keys.
4. One-to-many means one course can be associated with many student rows.
5. A separate courses table avoids repeating course names and helps keep course data consistent.
6. Normalization organizes data to reduce duplication and prevent update inconsistencies.
7. `INNER JOIN` returns rows with matching keys in both tables.
8. `LEFT JOIN` returns every left-table row plus matching right-table data, or `NULL` when no match exists.
9. `INNER JOIN` drops unmatched rows; `LEFT JOIN` preserves every left-side row.
10. `ON` specifies how rows from the tables match.
11. Aliases shorten queries and make references clearer, especially when joining tables.
12. The foreign-key constraint rejects the student insert; the app reports `Invalid course ID.`
13. A left-side row without a matching right-side row has `NULL` for right-table columns.
14. Use `LEFT JOIN` and filter where the student key is `NULL`.
15. Yes. A join can combine related rows before `GROUP BY` calculates per-course aggregates.

## Viva Questions

1. A foreign key points to a key in another table and enforces referential integrity.
2. `INNER JOIN` returns only matching rows.
3. `LEFT JOIN` returns every left-table row and matching right-side values where available.
4. `LEFT JOIN` students and filter `WHERE s.student_id IS NULL`.
5. It avoids repeating course names in every student record and ensures consistent course data.
6. One course can have many students, while each student references one course.
