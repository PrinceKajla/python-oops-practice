import sqlite3
from pathlib import Path

from course import Course
from student import Student


class DuplicateStudentError(ValueError):
    pass


class DuplicateCourseError(ValueError):
    pass


class Database:
    def __init__(self, database_name=None):
        self.database_name = (
            str(Path(__file__).with_name("student_management.db"))
            if database_name is None
            else database_name
        )
        self.connection = None

    def connect(self):
        if self.connection is None:
            self.connection = sqlite3.connect(self.database_name)
            self.connection.execute("PRAGMA foreign_keys = ON")
        return self.connection

    def _require_connection(self):
        if self.connection is None:
            raise RuntimeError("Connect to the database before using it.")
        return self.connection

    @staticmethod
    def _validate_course_name(course_name):
        if not isinstance(course_name, str) or not course_name.strip():
            raise ValueError("Course name cannot be empty.")
        return course_name.strip()

    @staticmethod
    def _validate_marks(min_marks):
        if (
            isinstance(min_marks, bool)
            or not isinstance(min_marks, (int, float))
            or not 0 <= min_marks <= 100
        ):
            raise ValueError("Invalid marks.")

    @staticmethod
    def _students_from_rows(rows):
        return [Student(*row) for row in rows]

    @staticmethod
    def _joined_student_query():
        return """
            SELECT s.student_id, s.name, s.age, s.course_id, s.marks, c.course_name
            FROM students AS s
            INNER JOIN courses AS c ON s.course_id = c.course_id
        """

    def create_course_table(self):
        connection = self._require_connection()
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS courses (
                course_id INTEGER PRIMARY KEY,
                course_name TEXT NOT NULL UNIQUE
            )
            """
        )
        connection.commit()

    def create_table(self):
        connection = self._require_connection()
        self.create_course_table()
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL CHECK (age > 0),
                course_id INTEGER NOT NULL,
                marks REAL NOT NULL CHECK (marks >= 0 AND marks <= 100),
                FOREIGN KEY (course_id) REFERENCES courses(course_id)
            )
            """
        )
        connection.commit()
        self.create_history_table()

    def create_history_table(self):
        connection = self._require_connection()
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS student_course_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                old_course_id INTEGER NOT NULL,
                new_course_id INTEGER NOT NULL,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (old_course_id) REFERENCES courses(course_id),
                FOREIGN KEY (new_course_id) REFERENCES courses(course_id)
            )
            """
        )
        connection.commit()

    def add_course(self, course):
        connection = self._require_connection()
        if not isinstance(course, Course):
            raise ValueError("A Course object is required.")
        course.validate()
        course_name = course.course_name.strip()
        try:
            connection.execute(
                "INSERT INTO courses (course_id, course_name) VALUES (?, ?)",
                (course.course_id, course_name),
            )
            connection.commit()
        except sqlite3.IntegrityError:
            connection.rollback()
            raise DuplicateCourseError("Course ID or name already exists.") from None
        except sqlite3.Error:
            connection.rollback()
            raise

    def get_all_courses(self):
        connection = self._require_connection()
        rows = connection.execute(
            "SELECT course_id, course_name FROM courses ORDER BY course_id"
        ).fetchall()
        return [Course(*row) for row in rows]

    def get_course_by_id(self, course_id):
        connection = self._require_connection()
        row = connection.execute(
            "SELECT course_id, course_name FROM courses WHERE course_id = ?",
            (course_id,),
        ).fetchone()
        return Course(*row) if row is not None else None

    def delete_course(self, course_id):
        connection = self._require_connection()
        try:
            cursor = connection.execute(
                "DELETE FROM courses WHERE course_id = ?",
                (course_id,),
            )
            connection.commit()
            return cursor.rowcount
        except sqlite3.IntegrityError:
            connection.rollback()
            raise ValueError("Cannot delete a course referenced by students or history.") from None
        except sqlite3.Error:
            connection.rollback()
            raise

    def add_student(self, student):
        connection = self._require_connection()
        if not isinstance(student, Student):
            raise ValueError("A Student object is required.")
        validated_student = Student(
            student.student_id,
            student.name,
            student.age,
            student.course_id,
            student.marks,
        )
        if self.get_course_by_id(validated_student.course_id) is None:
            raise ValueError("Invalid course ID.")
        try:
            connection.execute(
                """
                INSERT INTO students (student_id, name, age, course_id, marks)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    validated_student.student_id,
                    validated_student.name,
                    validated_student.age,
                    validated_student.course_id,
                    validated_student.marks,
                ),
            )
            connection.commit()
        except sqlite3.IntegrityError:
            connection.rollback()
            duplicate = connection.execute(
                "SELECT 1 FROM students WHERE student_id = ?",
                (validated_student.student_id,),
            ).fetchone()
            if duplicate is not None:
                raise DuplicateStudentError("Student ID already exists.") from None
            if self.get_course_by_id(validated_student.course_id) is None:
                raise ValueError("Invalid course ID.") from None
            raise ValueError("Student record violates a database constraint.") from None
        except sqlite3.Error:
            connection.rollback()
            raise

    def get_all_students(self):
        connection = self._require_connection()
        rows = connection.execute(
            self._joined_student_query() + " ORDER BY s.student_id"
        ).fetchall()
        return self._students_from_rows(rows)

    def get_student_by_id(self, student_id):
        connection = self._require_connection()
        row = connection.execute(
            self._joined_student_query() + " WHERE s.student_id = ?",
            (student_id,),
        ).fetchone()
        return Student(*row) if row is not None else None

    def update_student(self, student):
        connection = self._require_connection()
        if not isinstance(student, Student):
            raise ValueError("A Student object is required.")
        validated_student = Student(
            student.student_id,
            student.name,
            student.age,
            student.course_id,
            student.marks,
        )
        current_student = self.get_student_by_id(validated_student.student_id)
        if current_student is None:
            return 0
        if validated_student.course_id != current_student.course_id:
            raise ValueError("Use transfer_student_course() to change a student's course.")
        try:
            cursor = connection.execute(
                """
                UPDATE students
                SET name = ?, age = ?, marks = ?
                WHERE student_id = ?
                """,
                (
                    validated_student.name,
                    validated_student.age,
                    validated_student.marks,
                    validated_student.student_id,
                ),
            )
            connection.commit()
            return cursor.rowcount
        except sqlite3.Error:
            connection.rollback()
            raise

    def delete_student(self, student_id):
        connection = self._require_connection()
        try:
            cursor = connection.execute(
                "DELETE FROM students WHERE student_id = ?",
                (student_id,),
            )
            connection.commit()
            return cursor.rowcount
        except sqlite3.IntegrityError:
            connection.rollback()
            raise ValueError("Cannot delete a student with course transfer history.") from None
        except sqlite3.Error:
            connection.rollback()
            raise

    def get_students_by_course(self, course_name):
        connection = self._require_connection()
        course_name = self._validate_course_name(course_name)
        rows = connection.execute(
            self._joined_student_query() + " WHERE c.course_name = ? ORDER BY s.student_id",
            (course_name,),
        ).fetchall()
        return self._students_from_rows(rows)

    def get_students_by_marks(self, min_marks):
        connection = self._require_connection()
        self._validate_marks(min_marks)
        rows = connection.execute(
            self._joined_student_query() + " WHERE s.marks >= ? ORDER BY s.student_id",
            (min_marks,),
        ).fetchall()
        return self._students_from_rows(rows)

    def search_students_by_name(self, keyword):
        connection = self._require_connection()
        if not isinstance(keyword, str) or not keyword.strip():
            raise ValueError("Search keyword cannot be empty.")
        keyword = f"%{keyword.strip()}%"
        rows = connection.execute(
            self._joined_student_query() + " WHERE s.name LIKE ? ORDER BY s.student_id",
            (keyword,),
        ).fetchall()
        return self._students_from_rows(rows)

    def get_students_sorted_by_marks(self, desc=True):
        connection = self._require_connection()
        order = "DESC" if desc else "ASC"
        rows = connection.execute(
            self._joined_student_query() + f" ORDER BY s.marks {order}"
        ).fetchall()
        return self._students_from_rows(rows)

    def get_students_sorted_by_name(self):
        connection = self._require_connection()
        rows = connection.execute(
            self._joined_student_query() + " ORDER BY s.name COLLATE NOCASE"
        ).fetchall()
        return self._students_from_rows(rows)

    def get_top_students(self, limit):
        connection = self._require_connection()
        if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
            raise ValueError("Number of students must be greater than 0.")
        rows = connection.execute(
            self._joined_student_query() + " ORDER BY s.marks DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return self._students_from_rows(rows)

    def get_students_by_course_and_marks(self, course_name, min_marks):
        connection = self._require_connection()
        course_name = self._validate_course_name(course_name)
        self._validate_marks(min_marks)
        rows = connection.execute(
            self._joined_student_query()
            + " WHERE c.course_name = ? AND s.marks >= ? ORDER BY s.student_id",
            (course_name, min_marks),
        ).fetchall()
        return self._students_from_rows(rows)

    def get_students_by_either_course(self, first_course, second_course):
        connection = self._require_connection()
        first_course = self._validate_course_name(first_course)
        second_course = self._validate_course_name(second_course)
        rows = connection.execute(
            self._joined_student_query()
            + " WHERE c.course_name = ? OR c.course_name = ? ORDER BY s.student_id",
            (first_course, second_course),
        ).fetchall()
        return self._students_from_rows(rows)

    def get_students_with_courses(self):
        connection = self._require_connection()
        return connection.execute(
            """
            SELECT s.student_id, s.name, c.course_name, s.marks
            FROM students AS s
            INNER JOIN courses AS c ON s.course_id = c.course_id
            ORDER BY s.student_id
            """
        ).fetchall()

    def get_total_students(self):
        connection = self._require_connection()
        return connection.execute("SELECT COUNT(*) FROM students").fetchone()[0]

    def get_average_marks(self):
        connection = self._require_connection()
        return connection.execute("SELECT AVG(marks) FROM students").fetchone()[0]

    def get_total_marks(self):
        connection = self._require_connection()
        return connection.execute(
            "SELECT COALESCE(SUM(marks), 0) FROM students"
        ).fetchone()[0]

    def get_highest_marks(self):
        connection = self._require_connection()
        return connection.execute("SELECT MAX(marks) FROM students").fetchone()[0]

    def get_lowest_marks(self):
        connection = self._require_connection()
        return connection.execute("SELECT MIN(marks) FROM students").fetchone()[0]

    def get_course_statistics(self):
        connection = self._require_connection()
        return connection.execute(
            """
            SELECT c.course_name,
                   COUNT(s.student_id),
                   AVG(s.marks),
                   MAX(s.marks),
                   MIN(s.marks)
            FROM courses AS c
            LEFT JOIN students AS s ON c.course_id = s.course_id
            GROUP BY c.course_id, c.course_name
            ORDER BY c.course_id
            """
        ).fetchall()

    def get_course_average_marks(self):
        connection = self._require_connection()
        return connection.execute(
            """
            SELECT c.course_name, AVG(s.marks)
            FROM courses AS c
            INNER JOIN students AS s ON c.course_id = s.course_id
            GROUP BY c.course_id, c.course_name
            ORDER BY c.course_id
            """
        ).fetchall()

    def get_course_highest_marks(self):
        connection = self._require_connection()
        return connection.execute(
            """
            SELECT c.course_name, MAX(s.marks)
            FROM courses AS c
            INNER JOIN students AS s ON c.course_id = s.course_id
            GROUP BY c.course_id, c.course_name
            ORDER BY c.course_id
            """
        ).fetchall()

    def get_course_lowest_marks(self):
        connection = self._require_connection()
        return connection.execute(
            """
            SELECT c.course_name, MIN(s.marks)
            FROM courses AS c
            INNER JOIN students AS s ON c.course_id = s.course_id
            GROUP BY c.course_id, c.course_name
            ORDER BY c.course_id
            """
        ).fetchall()

    def get_course_average_marks_for_students_at_least(self, min_marks):
        connection = self._require_connection()
        self._validate_marks(min_marks)
        return connection.execute(
            """
            SELECT c.course_name, AVG(s.marks)
            FROM courses AS c
            INNER JOIN students AS s ON c.course_id = s.course_id
            WHERE s.marks >= ?
            GROUP BY c.course_id, c.course_name
            ORDER BY c.course_id
            """,
            (min_marks,),
        ).fetchall()

    def get_courses_above_average(self, min_average):
        connection = self._require_connection()
        if (
            isinstance(min_average, bool)
            or not isinstance(min_average, (int, float))
            or not 0 <= min_average <= 100
        ):
            raise ValueError("Invalid average.")
        return connection.execute(
            """
            SELECT c.course_name, AVG(s.marks) AS average_marks
            FROM courses AS c
            INNER JOIN students AS s ON c.course_id = s.course_id
            GROUP BY c.course_id, c.course_name
            HAVING AVG(s.marks) >= ?
            ORDER BY c.course_id
            """,
            (min_average,),
        ).fetchall()

    def get_courses_without_students(self):
        connection = self._require_connection()
        rows = connection.execute(
            """
            SELECT c.course_id, c.course_name
            FROM courses AS c
            LEFT JOIN students AS s ON c.course_id = s.course_id
            WHERE s.student_id IS NULL
            ORDER BY c.course_id
            """
        ).fetchall()
        return [Course(*row) for row in rows]

    def begin_transaction(self):
        connection = self._require_connection()
        if connection.in_transaction:
            raise RuntimeError("A transaction is already active.")
        connection.execute("BEGIN")

    def commit(self):
        self._require_connection().commit()

    def rollback(self):
        self._require_connection().rollback()

    def transfer_student_course(self, student_id, new_course_id):
        connection = self._require_connection()
        if isinstance(student_id, bool) or not isinstance(student_id, int):
            raise ValueError("Student ID must be an integer.")
        if isinstance(new_course_id, bool) or not isinstance(new_course_id, int):
            raise ValueError("Course ID must be an integer.")

        student = self.get_student_by_id(student_id)
        if student is None:
            raise ValueError("Student not found.")
        if self.get_course_by_id(new_course_id) is None:
            raise ValueError("Invalid course ID.")
        if student.course_id == new_course_id:
            raise ValueError("Student is already enrolled in this course.")

        self.begin_transaction()
        try:
            current_student = self.get_student_by_id(student_id)
            if current_student is None:
                raise ValueError("Student not found.")
            if self.get_course_by_id(new_course_id) is None:
                raise ValueError("Invalid course ID.")
            if current_student.course_id == new_course_id:
                raise ValueError("Student is already enrolled in this course.")

            cursor = connection.execute(
                "UPDATE students SET course_id = ? WHERE student_id = ?",
                (new_course_id, student_id),
            )
            if cursor.rowcount != 1:
                raise ValueError("Student not found.")
            history_cursor = connection.execute(
                """
                INSERT INTO student_course_history
                    (student_id, old_course_id, new_course_id)
                VALUES (?, ?, ?)
                """,
                (student_id, current_student.course_id, new_course_id),
            )
            self.commit()
            return history_cursor.lastrowid
        except Exception:
            self.rollback()
            raise

    def get_course_history(self):
        connection = self._require_connection()
        return connection.execute(
            """
            SELECT h.history_id, h.student_id, s.name,
                   old_course.course_name, new_course.course_name, h.changed_at
            FROM student_course_history AS h
            INNER JOIN students AS s ON h.student_id = s.student_id
            INNER JOIN courses AS old_course ON h.old_course_id = old_course.course_id
            INNER JOIN courses AS new_course ON h.new_course_id = new_course.course_id
            ORDER BY h.history_id
            """
        ).fetchall()

    def get_student_course_history(self, student_id):
        connection = self._require_connection()
        return connection.execute(
            """
            SELECT h.history_id, h.student_id, s.name,
                   old_course.course_name, new_course.course_name, h.changed_at
            FROM student_course_history AS h
            INNER JOIN students AS s ON h.student_id = s.student_id
            INNER JOIN courses AS old_course ON h.old_course_id = old_course.course_id
            INNER JOIN courses AS new_course ON h.new_course_id = new_course.course_id
            WHERE h.student_id = ?
            ORDER BY h.history_id
            """,
            (student_id,),
        ).fetchall()

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
