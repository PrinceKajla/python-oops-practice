import sqlite3

from database import Database, DuplicateStudentError
from student import Student


def _read_integer(prompt, error_message):
    try:
        return int(input(prompt).strip())
    except ValueError:
        raise ValueError(error_message) from None


def _read_number(prompt, error_message):
    try:
        return float(input(prompt).strip())
    except ValueError:
        raise ValueError(error_message) from None


def add_student(database):
    try:
        student = Student(
            _read_integer("Student ID: ", "Student ID must be an integer."),
            input("Name: "),
            _read_integer("Age: ", "Age validation error: enter an integer."),
            input("Course: "),
            _read_number("Marks: ", "Marks validation error: enter a number."),
        )
        database.add_student(student)
        print("Student added successfully.")
    except DuplicateStudentError as error:
        print(error)
    except ValueError as error:
        print(error)
    except sqlite3.Error:
        print("Database operation failed.")


def show_students(database):
    try:
        students = database.get_all_students()
        if not students:
            print("No students found.")
            return
        for student in students:
            print(student.display())
    except sqlite3.Error:
        print("Database operation failed.")


def search_student(database):
    try:
        student_id = _read_integer(
            "Student ID to search: ", "Student ID must be an integer."
        )
    except ValueError as error:
        print(error)
        return

    try:
        student = database.get_student_by_id(student_id)
        if student is None:
            print("Student not found.")
        else:
            print(student.display())
    except sqlite3.Error:
        print("Database operation failed.")


def run_menu(database):
    while True:
        print("\nUniversity Student Management System")
        print("1. Add student")
        print("2. List all students")
        print("3. Search student by ID")
        print("4. Exit")

        choice = input("Choose an option: ").strip()
        if choice == "1":
            add_student(database)
        elif choice == "2":
            show_students(database)
        elif choice == "3":
            search_student(database)
        elif choice == "4":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Enter 1, 2, 3, or 4.")


def main():
    database = Database()
    try:
        database.connect()
        database.create_table()
        run_menu(database)
    except sqlite3.Error:
        print("Database operation failed.")
    finally:
        database.close()


if __name__ == "__main__":
    main()