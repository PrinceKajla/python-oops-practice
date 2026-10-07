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


def _read_student_details(student_id):
    return Student(
        student_id,
        input("Name: "),
        _read_integer("Age: ", "Age validation error: enter an integer."),
        input("Course: "),
        _read_number("Marks: ", "Marks validation error: enter a number."),
    )


def add_student(database):
    try:
        student_id = _read_integer("Student ID: ", "Student ID must be an integer.")
        student = _read_student_details(student_id)
        database.add_student(student)
        print("Student added successfully.")
    except (DuplicateStudentError, ValueError) as error:
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
        student = database.get_student_by_id(student_id)
        if student is None:
            print("Student not found.")
        else:
            print(student.display())
    except ValueError as error:
        print(error)
    except sqlite3.Error:
        print("Database operation failed.")


def update_student(database):
    try:
        student_id = _read_integer(
            "Student ID to update: ", "Student ID must be an integer."
        )
        existing_student = database.get_student_by_id(student_id)
        if existing_student is None:
            print("Student not found.")
            return

        print("Current student:")
        print(existing_student.display())
        updated_student = _read_student_details(student_id)
        rowcount = database.update_student(updated_student)
        if rowcount == 0:
            print("Student not found.")
        else:
            print("Student updated successfully.")
    except ValueError as error:
        print(error)
    except sqlite3.Error:
        print("Database operation failed.")


def delete_student(database):
    try:
        student_id = _read_integer(
            "Student ID to delete: ", "Student ID must be an integer."
        )
        student = database.get_student_by_id(student_id)
        if student is None:
            print("Student not found.")
            return

        print("Student to delete:")
        print(student.display())
        confirmation = input("Delete this student? Enter yes to confirm: ").strip()
        if confirmation.lower() != "yes":
            print("Deletion cancelled.")
            return

        if database.delete_student(student_id) == 0:
            print("Student not found.")
        else:
            print("Student deleted successfully.")
    except ValueError as error:
        print(error)
    except sqlite3.Error:
        print("Database operation failed.")


def run_menu(database):
    while True:
        print("\nStudent Management System")
        print("1. Add Student")
        print("2. View All Students")
        print("3. Search Student")
        print("4. Update Student")
        print("5. Delete Student")
        print("6. Exit")

        choice = input("Choose an option: ").strip()
        if choice == "1":
            add_student(database)
        elif choice == "2":
            show_students(database)
        elif choice == "3":
            search_student(database)
        elif choice == "4":
            update_student(database)
        elif choice == "5":
            delete_student(database)
        elif choice == "6":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Enter a number from 1 to 6.")


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
