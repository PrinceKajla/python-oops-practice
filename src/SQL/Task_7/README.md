# Database Transactions and ACID

**Task ID:** SQL-PY-007

## Project Files

- `main.py` runs the student, course, and transfer-history menus.
- `database.py` manages the relational schema and transaction boundaries.
- `student.py` models students with a `course_id` foreign key.
- `course.py` models and validates courses.
- `student_management.db` is created beside these files on first run.

## Run

From this folder, run:

```console
python main.py
```

Create the courses and students before transferring a student. For the sample transfer, add BCA (ID 1), MCA (ID 3), and Rahul enrolled in BCA.

## Course Transfer Transaction

`transfer_student_course(student_id, new_course_id)` validates the student and target course, rejects transfers to the current course, then runs both writes in one explicit transaction:

1. `BEGIN`
2. `UPDATE students SET course_id = ? WHERE student_id = ?`
3. `INSERT INTO student_course_history (student_id, old_course_id, new_course_id) VALUES (?, ?, ?)`
4. `COMMIT`

If either write fails, the method rolls back and re-raises the error. The student remains in the original course, and no history row is committed. Foreign-key enforcement is enabled when the database connection opens. Ordinary student edits cannot change `course_id`; use the transfer option so course changes are recorded.

`get_course_history()` returns all transfers, while `get_student_course_history(student_id)` filters history for one student. Course and student deletion are restricted when referenced by history, preserving the audit trail.

## Required Behavior Checks

1. Transfer Rahul from BCA to MCA; verify his current course and one history row.
2. Transfer a nonexistent student; expect `Student not found.` and no change.
3. Transfer to course ID 99; expect `Invalid course ID.` and no change.
4. Transfer BCA to BCA; expect `Student is already enrolled in this course.` and no change.
5. To simulate a failure after the UPDATE but during history insertion, create a trigger before transferring:

```sql
CREATE TRIGGER fail_course_history
BEFORE INSERT ON student_course_history
BEGIN
    SELECT RAISE(ABORT, 'simulated history failure');
END;
```

After the attempted transfer raises an error, verify the student still has the original `course_id` and the history table has no new row. Remove the trigger after the check with `DROP TRIGGER fail_course_history`.

## ACID Properties

- Atomicity: both the student update and history insert commit together, or neither does.
- Consistency: foreign keys and value constraints remain valid before and after the transaction.
- Isolation: SQLite controls concurrent access so another transaction cannot observe uncommitted transfer changes.
- Durability: once committed, the new enrollment and its history persist.

## Assignment Questions

1. A transaction is a group of database operations treated as one unit.
2. `COMMIT` permanently saves the current transaction's changes.
3. `ROLLBACK` cancels uncommitted changes.
4. Transactions prevent partial changes when multiple operations must succeed together.
5. For a course transfer, changing enrollment and inserting history must both happen, or neither should happen.
6. Atomicity is all-or-nothing; consistency preserves constraints; isolation prevents improper interference; durability preserves committed changes.
7. An exception before commit leaves the work uncommitted; the error handler should roll it back.
8. A partial update occurs when only some operations in a related set are applied.
9. Validate inputs first to reject invalid work before beginning a transaction or making changes.
10. `COMMIT` saves uncommitted work; `ROLLBACK` discards it.
11. `UPDATE students SET course_id = ? WHERE student_id = ?`.
12. `INSERT INTO student_course_history (student_id, old_course_id, new_course_id) VALUES (?, ?, ?)`.
13. Join history to students and to courses twice, once for the old course and once for the new course; the application does this in `get_course_history()`.
14. `SELECT s.name, old_course.course_name, new_course.course_name, h.changed_at FROM student_course_history AS h JOIN students AS s ON h.student_id = s.student_id JOIN courses AS old_course ON h.old_course_id = old_course.course_id JOIN courses AS new_course ON h.new_course_id = new_course.course_id`.

## Viva Questions

1. It prevents partial results when multiple related database operations must be treated as one unit.
2. `COMMIT` makes transaction changes permanent.
3. `ROLLBACK` cancels uncommitted changes.
4. A bank transfer must debit one account and credit another together.
5. ACID means Atomicity, Consistency, Isolation, and Durability.
6. Atomicity means all operations succeed together or none do.
