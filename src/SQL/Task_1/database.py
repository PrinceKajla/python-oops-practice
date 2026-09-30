import sqlite3

from student import Student


class Database:
    def __init__(self, database_name="student_management.db"):
        self.database_name = database_name
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
                student_id INTEGER,
                name TEXT,
                age INTEGER,
                course TEXT,
                marks REAL
            )
            """
        )
        connection.commit()

    def add_student(self, student):
        connection = self._require_connection()
        connection.execute(
            """
            INSERT INTO students (student_id, name, age, course, marks)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                student.student_id,
                student.name,
                student.age,
                student.course,
                student.marks,
            ),
        )
        connection.commit()

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