import sqlite3

from database import Database
from student import Student


def add_student(database):
    try:
        student = Student(
            int(input("Student ID: ").strip()),
            input("Name: "),
            int(input("Age: ").strip()),
            input("Course: "),
            float(input("Marks: ").strip()),
        )
        database.add_student(student)
        print("Student stored successfully.")
    except ValueError as error:
        print(f"Invalid student data: {error}")
    except sqlite3.Error as error:
        print(f"Database error: {error}")


def show_students(database):
    try:
        students = database.get_all_students()
        if not students:
            print("No students found.")
            return
        for student in students:
            print(student.display())
    except sqlite3.Error as error:
        print(f"Database error: {error}")


def search_student(database):
    try:
        student_id = int(input("Student ID to search: ").strip())
    except ValueError:
        print("Invalid input: student ID must be an integer.")
        return

    try:
        student = database.get_student_by_id(student_id)
        if student is None:
            print("Student not found.")
        else:
            print(student.display())
    except sqlite3.Error as error:
        print(f"Database error: {error}")


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
    except sqlite3.Error as error:
        print(f"Database error: {error}")
    finally:
        database.close()


if __name__ == "__main__":
    main()