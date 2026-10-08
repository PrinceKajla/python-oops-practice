import psycopg

from config import get_database_config
from course import Course
from student import Student


class DatabaseConnectionError(ConnectionError):
    pass


class DuplicateStudentError(ValueError):
    pass


class DuplicateCourseError(ValueError):
    pass


class Database:
    def __init__(self, connection_config=None):
        self.connection_config = connection_config
        self.connection = None
        self._transaction_active = False

    def connect(self):
        if self.connection is not None and not self.connection.closed:
            return self.connection
        try:
            config = self.connection_config or get_database_config()
            self.connection = psycopg.connect(**config, connect_timeout=5)
            self._transaction_active = False
        except psycopg.OperationalError as error:
            sqlstate = getattr(error, "sqlstate", None)
            if sqlstate is not None and sqlstate.startswith("28"):
                message = "Database authentication failed."
            else:
                message = "Unable to connect to database."
            raise DatabaseConnectionError(message) from None
        return self.connection

    def _require_connection(self):
        if self.connection is None or self.connection.closed:
            raise RuntimeError("Connect to the database before using it.")
        return self.connection

    def execute_query(self, query, parameters=None):
        cursor = self._require_connection().cursor()
        try:
            cursor.execute(query, parameters)
            return cursor
        except Exception:
            cursor.close()
            raise

    def fetch_one(self, query, parameters=None):
        with self.execute_query(query, parameters) as cursor:
            row = cursor.fetchone()
        if not self._transaction_active:
            self.commit()
        return row

    def fetch_all(self, query, parameters=None):
        with self.execute_query(query, parameters) as cursor:
            rows = cursor.fetchall()
        if not self._transaction_active:
            self.commit()
        return rows

    def commit(self):
        self._require_connection().commit()
        self._transaction_active = False

    def rollback(self):
        self._require_connection().rollback()
        self._transaction_active = False

    def create_tables(self):
        connection = self._require_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS courses (
                        course_id SERIAL PRIMARY KEY,
                        course_name VARCHAR(100) NOT NULL UNIQUE
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS students (
                        student_id INTEGER PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        age INTEGER NOT NULL CHECK (age > 0),
                        course_id INTEGER NOT NULL
                            REFERENCES courses(course_id),
                        marks NUMERIC(5, 2) NOT NULL
                            CHECK (marks >= 0 AND marks <= 100)
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS student_course_history (
                        history_id SERIAL PRIMARY KEY,
                        student_id INTEGER NOT NULL
                            REFERENCES students(student_id),
                        old_course_id INTEGER NOT NULL
                            REFERENCES courses(course_id),
                        new_course_id INTEGER NOT NULL
                            REFERENCES courses(course_id),
                        changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            self.commit()
        except psycopg.Error:
            self.rollback()
            raise

    @staticmethod
    def _joined_student_query():
        return """
            SELECT s.student_id, s.name, s.age, s.course_id, s.marks, c.course_name
            FROM students AS s
            INNER JOIN courses AS c ON s.course_id = c.course_id
        """

    @staticmethod
    def _students_from_rows(rows):
        return [Student(*row) for row in rows]

    @staticmethod
    def _validate_course_name(course_name):
        if not isinstance(course_name, str) or not course_name.strip():
            raise ValueError("Course name cannot be empty.")
        return course_name.strip()

    @staticmethod
    def _validate_marks(marks):
        if (
            isinstance(marks, bool)
            or not isinstance(marks, (int, float))
            or not 0 <= marks <= 100
        ):
            raise ValueError("Invalid marks.")

    def add_course(self, course):
        if not isinstance(course, Course):
            raise ValueError("A Course object is required.")
        course.validate()
        try:
            if course.course_id is None:
                row = self.fetch_one(
                    "INSERT INTO courses (course_name) VALUES (%s) RETURNING course_id",
                    (course.course_name.strip(),),
                )
                course.course_id = row[0]
            else:
                self.execute_query(
                    "INSERT INTO courses (course_id, course_name) VALUES (%s, %s)",
                    (course.course_id, course.course_name.strip()),
                ).close()
                self.execute_query(
                    """
                    SELECT setval(
                        pg_get_serial_sequence('courses', 'course_id'),
                        (SELECT MAX(course_id) FROM courses),
                        true
                    )
                    """
                ).close()
            self.commit()
            return course.course_id
        except psycopg.IntegrityError as error:
            self.rollback()
            if error.sqlstate == "23505":
                raise DuplicateCourseError("Course name or ID already exists.") from None
            raise
        except psycopg.Error:
            self.rollback()
            raise

    def get_all_courses(self):
        return [
            Course(*row)
            for row in self.fetch_all(
                "SELECT course_id, course_name FROM courses ORDER BY course_id"
            )
        ]

    def get_course_by_id(self, course_id):
        row = self.fetch_one(
            "SELECT course_id, course_name FROM courses WHERE course_id = %s",
            (course_id,),
        )
        return Course(*row) if row is not None else None

    def delete_course(self, course_id):
        try:
            cursor = self.execute_query(
                "DELETE FROM courses WHERE course_id = %s", (course_id,)
            )
            rowcount = cursor.rowcount
            cursor.close()
            self.commit()
            return rowcount
        except psycopg.IntegrityError:
            self.rollback()
            raise ValueError(
                "Cannot delete a course referenced by students or history."
            ) from None
        except psycopg.Error:
            self.rollback()
            raise

    def add_student(self, student):
        if not isinstance(student, Student):
            raise ValueError("A Student object is required.")
        valid = Student(
            student.student_id, student.name, student.age, student.course_id, student.marks
        )
        if self.get_course_by_id(valid.course_id) is None:
            raise ValueError("Invalid course ID.")
        try:
            self.execute_query(
                """
                INSERT INTO students (student_id, name, age, course_id, marks)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (valid.student_id, valid.name, valid.age, valid.course_id, valid.marks),
            ).close()
            self.commit()
        except psycopg.IntegrityError as error:
            self.rollback()
            if error.sqlstate == "23505":
                raise DuplicateStudentError("Student ID already exists.") from None
            if error.sqlstate == "23503":
                raise ValueError("Invalid course ID.") from None
            raise ValueError("Student record violates a database constraint.") from None
        except psycopg.Error:
            self.rollback()
            raise

    def get_all_students(self):
        rows = self.fetch_all(self._joined_student_query() + " ORDER BY s.student_id")
        return self._students_from_rows(rows)

    def get_student_by_id(self, student_id):
        row = self.fetch_one(
            self._joined_student_query() + " WHERE s.student_id = %s", (student_id,)
        )
        return Student(*row) if row is not None else None

    def update_student(self, student):
        if not isinstance(student, Student):
            raise ValueError("A Student object is required.")
        valid = Student(
            student.student_id, student.name, student.age, student.course_id, student.marks
        )
        current = self.get_student_by_id(valid.student_id)
        if current is None:
            return 0
        if valid.course_id != current.course_id:
            raise ValueError("Use transfer_student_course() to change a student's course.")
        try:
            cursor = self.execute_query(
                """
                UPDATE students SET name = %s, age = %s, marks = %s
                WHERE student_id = %s
                """,
                (valid.name, valid.age, valid.marks, valid.student_id),
            )
            rowcount = cursor.rowcount
            cursor.close()
            self.commit()
            return rowcount
        except psycopg.Error:
            self.rollback()
            raise

    def delete_student(self, student_id):
        try:
            cursor = self.execute_query(
                "DELETE FROM students WHERE student_id = %s", (student_id,)
            )
            rowcount = cursor.rowcount
            cursor.close()
            self.commit()
            return rowcount
        except psycopg.IntegrityError:
            self.rollback()
            raise ValueError(
                "Cannot delete a student with course transfer history."
            ) from None
        except psycopg.Error:
            self.rollback()
            raise

    def get_students_by_course(self, course_name):
        course_name = self._validate_course_name(course_name)
        rows = self.fetch_all(
            self._joined_student_query()
            + " WHERE c.course_name = %s ORDER BY s.student_id",
            (course_name,),
        )
        return self._students_from_rows(rows)

    def get_students_by_marks(self, min_marks):
        self._validate_marks(min_marks)
        rows = self.fetch_all(
            self._joined_student_query() + " WHERE s.marks >= %s ORDER BY s.student_id",
            (min_marks,),
        )
        return self._students_from_rows(rows)

    def get_students_by_course_and_marks(self, course_name, min_marks):
        course_name = self._validate_course_name(course_name)
        self._validate_marks(min_marks)
        rows = self.fetch_all(
            self._joined_student_query()
            + " WHERE c.course_name = %s AND s.marks >= %s ORDER BY s.student_id",
            (course_name, min_marks),
        )
        return self._students_from_rows(rows)

    def get_students_by_either_course(self, first_course, second_course):
        first_course = self._validate_course_name(first_course)
        second_course = self._validate_course_name(second_course)
        rows = self.fetch_all(
            self._joined_student_query()
            + " WHERE c.course_name = %s OR c.course_name = %s ORDER BY s.student_id",
            (first_course, second_course),
        )
        return self._students_from_rows(rows)

    def search_students_by_name(self, keyword):
        if not isinstance(keyword, str) or not keyword.strip():
            raise ValueError("Search keyword cannot be empty.")
        rows = self.fetch_all(
            self._joined_student_query()
            + " WHERE s.name ILIKE %s ORDER BY s.student_id",
            (f"%{keyword.strip()}%",),
        )
        return self._students_from_rows(rows)

    def get_students_sorted_by_marks(self, desc=True):
        order = "DESC" if desc else "ASC"
        rows = self.fetch_all(
            self._joined_student_query() + f" ORDER BY s.marks {order}"
        )
        return self._students_from_rows(rows)

    def get_students_sorted_by_name(self):
        rows = self.fetch_all(
            self._joined_student_query() + " ORDER BY LOWER(s.name), s.student_id"
        )
        return self._students_from_rows(rows)

    def get_top_students(self, limit):
        if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
            raise ValueError("Number of students must be greater than 0.")
        rows = self.fetch_all(
            self._joined_student_query() + " ORDER BY s.marks DESC LIMIT %s",
            (limit,),
        )
        return self._students_from_rows(rows)

    def get_students_with_courses(self):
        return self.fetch_all(
            """
            SELECT s.student_id, s.name, c.course_name, s.marks
            FROM students AS s
            INNER JOIN courses AS c ON s.course_id = c.course_id
            ORDER BY s.student_id
            """
        )

    def get_total_students(self):
        return self.fetch_one("SELECT COUNT(*) FROM students")[0]

    def get_average_marks(self):
        return self.fetch_one("SELECT AVG(marks) FROM students")[0]

    def get_total_marks(self):
        return self.fetch_one("SELECT COALESCE(SUM(marks), 0) FROM students")[0]

    def get_highest_marks(self):
        return self.fetch_one("SELECT MAX(marks) FROM students")[0]

    def get_lowest_marks(self):
        return self.fetch_one("SELECT MIN(marks) FROM students")[0]

    def get_course_statistics(self):
        return self.fetch_all(
            """
            SELECT c.course_name, COUNT(s.student_id), AVG(s.marks),
                   MAX(s.marks), MIN(s.marks)
            FROM courses AS c
            LEFT JOIN students AS s ON c.course_id = s.course_id
            GROUP BY c.course_id, c.course_name
            ORDER BY c.course_id
            """
        )

    def get_course_average_marks(self):
        return self.fetch_all(
            """
            SELECT c.course_name, AVG(s.marks)
            FROM courses AS c
            INNER JOIN students AS s ON c.course_id = s.course_id
            GROUP BY c.course_id, c.course_name
            ORDER BY c.course_id
            """
        )

    def get_course_highest_marks(self):
        return self.fetch_all(
            """
            SELECT c.course_name, MAX(s.marks)
            FROM courses AS c
            INNER JOIN students AS s ON c.course_id = s.course_id
            GROUP BY c.course_id, c.course_name
            ORDER BY c.course_id
            """
        )

    def get_course_lowest_marks(self):
        return self.fetch_all(
            """
            SELECT c.course_name, MIN(s.marks)
            FROM courses AS c
            INNER JOIN students AS s ON c.course_id = s.course_id
            GROUP BY c.course_id, c.course_name
            ORDER BY c.course_id
            """
        )

    def get_course_average_marks_for_students_at_least(self, min_marks):
        self._validate_marks(min_marks)
        return self.fetch_all(
            """
            SELECT c.course_name, AVG(s.marks)
            FROM courses AS c
            INNER JOIN students AS s ON c.course_id = s.course_id
            WHERE s.marks >= %s
            GROUP BY c.course_id, c.course_name
            ORDER BY c.course_id
            """,
            (min_marks,),
        )

    def get_courses_above_average(self, min_average):
        self._validate_marks(min_average)
        return self.fetch_all(
            """
            SELECT c.course_name, AVG(s.marks) AS average_marks
            FROM courses AS c
            INNER JOIN students AS s ON c.course_id = s.course_id
            GROUP BY c.course_id, c.course_name
            HAVING AVG(s.marks) >= %s
            ORDER BY c.course_id
            """,
            (min_average,),
        )

    def get_courses_without_students(self):
        return [
            Course(*row)
            for row in self.fetch_all(
                """
                SELECT c.course_id, c.course_name
                FROM courses AS c
                LEFT JOIN students AS s ON c.course_id = s.course_id
                WHERE s.student_id IS NULL
                ORDER BY c.course_id
                """
            )
        ]

    def begin_transaction(self):
        connection = self._require_connection()
        if self._transaction_active:
            raise RuntimeError("A transaction is already active.")
        # PostgreSQL starts a transaction for reads too; finish that read-only
        # transaction before beginning the explicit transfer transaction.
        connection.commit()
        connection.execute("BEGIN").close()
        self._transaction_active = True

    def transfer_student_course(self, student_id, new_course_id):
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
            row = self.fetch_one(
                "SELECT course_id FROM students WHERE student_id = %s FOR UPDATE",
                (student_id,),
            )
            if row is None:
                raise ValueError("Student not found.")
            old_course_id = row[0]
            if old_course_id == new_course_id:
                raise ValueError("Student is already enrolled in this course.")
            cursor = self.execute_query(
                "UPDATE students SET course_id = %s WHERE student_id = %s",
                (new_course_id, student_id),
            )
            if cursor.rowcount != 1:
                cursor.close()
                raise ValueError("Student not found.")
            cursor.close()
            history = self.fetch_one(
                """
                INSERT INTO student_course_history
                    (student_id, old_course_id, new_course_id)
                VALUES (%s, %s, %s)
                RETURNING history_id
                """,
                (student_id, old_course_id, new_course_id),
            )
            self.commit()
            return history[0]
        except Exception:
            self.rollback()
            raise

    def get_course_history(self, student_id=None):
        query = """
            SELECT h.history_id, h.student_id, s.name,
                   old_course.course_name, new_course.course_name, h.changed_at
            FROM student_course_history AS h
            INNER JOIN students AS s ON h.student_id = s.student_id
            INNER JOIN courses AS old_course ON h.old_course_id = old_course.course_id
            INNER JOIN courses AS new_course ON h.new_course_id = new_course.course_id
        """
        if student_id is None:
            return self.fetch_all(query + " ORDER BY h.history_id")
        return self.fetch_all(
            query + " WHERE h.student_id = %s ORDER BY h.history_id", (student_id,)
        )

    def close(self):
        if self.connection is not None and not self.connection.closed:
            if self._transaction_active:
                self.connection.rollback()
            self.connection.close()
        self.connection = None
        self._transaction_active = False
