import sqlite3
from pathlib import Path

from student import Student


class DuplicateStudentError(ValueError):
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
        return self.connection

    def _require_connection(self):
        if self.connection is None:
            raise RuntimeError("Connect to the database before using it.")
        return self.connection

    @staticmethod
    def _validate_course(course):
        if not isinstance(course, str) or not course.strip():
            raise ValueError("Course cannot be empty.")
        return course.strip()

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

    def create_table(self):
        connection = self._require_connection()
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL CHECK (age > 0),
                course TEXT NOT NULL,
                marks REAL NOT NULL CHECK (marks >= 0 AND marks <= 100)
            )
            """
        )
        connection.commit()

    def add_student(self, student):
        connection = self._require_connection()
        validated_student = Student(
            student.student_id,
            student.name,
            student.age,
            student.course,
            student.marks,
        )
        try:
            connection.execute(
                """
                INSERT INTO students (student_id, name, age, course, marks)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    validated_student.student_id,
                    validated_student.name,
                    validated_student.age,
                    validated_student.course,
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
            raise ValueError("Student record violates a database constraint.") from None
        except sqlite3.Error:
            connection.rollback()
            raise

    def get_all_students(self):
        connection = self._require_connection()
        rows = connection.execute(
            "SELECT * FROM students ORDER BY student_id"
        ).fetchall()
        return self._students_from_rows(rows)

    def get_student_by_id(self, student_id):
        connection = self._require_connection()
        row = connection.execute(
            "SELECT * FROM students WHERE student_id = ?",
            (student_id,),
        ).fetchone()
        return Student(*row) if row is not None else None

    def update_student(self, student):
        connection = self._require_connection()
        validated_student = Student(
            student.student_id,
            student.name,
            student.age,
            student.course,
            student.marks,
        )
        try:
            cursor = connection.execute(
                """
                UPDATE students
                SET name = ?, age = ?, course = ?, marks = ?
                WHERE student_id = ?
                """,
                (
                    validated_student.name,
                    validated_student.age,
                    validated_student.course,
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
        except sqlite3.Error:
            connection.rollback()
            raise

    def get_students_by_course(self, course):
        connection = self._require_connection()
        course = self._validate_course(course)
        rows = connection.execute(
            "SELECT * FROM students WHERE course = ?",
            (course,),
        ).fetchall()
        return self._students_from_rows(rows)

    def get_students_by_marks(self, min_marks):
        connection = self._require_connection()
        self._validate_marks(min_marks)
        rows = connection.execute(
            "SELECT * FROM students WHERE marks >= ?",
            (min_marks,),
        ).fetchall()
        return self._students_from_rows(rows)

    def search_students_by_name(self, keyword):
        connection = self._require_connection()
        if not isinstance(keyword, str) or not keyword.strip():
            raise ValueError("Search keyword cannot be empty.")
        keyword = f"%{keyword.strip()}%"
        rows = connection.execute(
            "SELECT * FROM students WHERE name LIKE ?",
            (keyword,),
        ).fetchall()
        return self._students_from_rows(rows)

    def get_students_sorted_by_marks(self, desc=True):
        connection = self._require_connection()
        order = "DESC" if desc else "ASC"
        rows = connection.execute(
            f"SELECT * FROM students ORDER BY marks {order}"
        ).fetchall()
        return self._students_from_rows(rows)

    def get_top_students(self, limit):
        connection = self._require_connection()
        if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
            raise ValueError("Number of students must be greater than 0.")
        rows = connection.execute(
            "SELECT * FROM students ORDER BY marks DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return self._students_from_rows(rows)

    def get_students_by_course_and_marks(self, course, min_marks):
        connection = self._require_connection()
        course = self._validate_course(course)
        self._validate_marks(min_marks)
        rows = connection.execute(
            "SELECT * FROM students WHERE course = ? AND marks >= ?",
            (course, min_marks),
        ).fetchall()
        return self._students_from_rows(rows)

    def get_students_by_either_course(self, first_course, second_course):
        connection = self._require_connection()
        first_course = self._validate_course(first_course)
        second_course = self._validate_course(second_course)
        rows = connection.execute(
            "SELECT * FROM students WHERE course = ? OR course = ?",
            (first_course, second_course),
        ).fetchall()
        return self._students_from_rows(rows)

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
