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

    def get_all_students(self):
        connection = self._require_connection()
        rows = connection.execute(
            "SELECT student_id, name, age, course, marks FROM students "
            "ORDER BY student_id"
        ).fetchall()
        return [Student(*row) for row in rows]

    def get_student_by_id(self, student_id):
        connection = self._require_connection()
        row = connection.execute(
            "SELECT student_id, name, age, course, marks "
            "FROM students WHERE student_id = ?",
            (student_id,),
        ).fetchone()
        return Student(*row) if row is not None else None

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None