import psycopg

from config import DatabaseConfigurationError
from course import Course
from database import (
    Database,
    DatabaseConnectionError,
)
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


def _read_student_details(student_id, course_id=None):
    if course_id is None:
        course_id = _read_integer("Course ID: ", "Course ID must be an integer.")
    return Student(
        student_id,
        input("Name: "),
        _read_integer("Age: ", "Age validation error: enter an integer."),
        course_id,
        _read_number("Marks: ", "Marks validation error: enter a number."),
    )


def _print_students(students):
    if not students:
        print("No students found.")
        return
    for student in students:
        print(student.display())


def _run_action(database, action):
    try:
        action(database)
    except ValueError as error:
        print(error)
    except psycopg.Error:
        database.rollback()
        print("Database operation failed.")


def add_course(database):
    name = input("Course name: ")
    course = Course(None, name)
    course_id = database.add_course(course)
    print(f"Course added successfully. Course ID: {course_id}")


def show_courses(database):
    courses = database.get_all_courses()
    if not courses:
        print("No courses found.")
        return
    for course in courses:
        print(course.display())


def add_student(database):
    student_id = _read_integer("Student ID: ", "Student ID must be an integer.")
    database.add_student(_read_student_details(student_id))
    print("Student added successfully.")


def show_students(database):
    rows = database.get_students_with_courses()
    if not rows:
        print("No students found.")
        return
    for student_id, name, course_name, marks in rows:
        print(
            f"ID: {student_id} | Name: {name} | Course: {course_name} "
            f"| Marks: {marks:g}"
        )


def search_student(database):
    student_id = _read_integer("Student ID to search: ", "Student ID must be an integer.")
    student = database.get_student_by_id(student_id)
    print("Student not found." if student is None else student.display())


def search_by_course(database):
    _print_students(database.get_students_by_course(input("Course name: ")))


def search_by_marks(database):
    marks = _read_number("Minimum marks (0-100): ", "Invalid marks.")
    _print_students(database.get_students_by_marks(marks))


def search_by_name(database):
    _print_students(database.search_students_by_name(input("Name keyword: ")))


def sort_students(database):
    print("Sort by: 1. Marks highest first  2. Marks lowest first  3. Name")
    choice = input("Choose a sort order: ").strip()
    if choice == "1":
        _print_students(database.get_students_sorted_by_marks(desc=True))
    elif choice == "2":
        _print_students(database.get_students_sorted_by_marks(desc=False))
    elif choice == "3":
        _print_students(database.get_students_sorted_by_name())
    else:
        print("Invalid sorting option.")


def update_student(database):
    student_id = _read_integer("Student ID to update: ", "Student ID must be an integer.")
    current = database.get_student_by_id(student_id)
    if current is None:
        print("Student not found.")
        return
    updated = Student(
        student_id,
        input("Name: "),
        _read_integer("Age: ", "Age validation error: enter an integer."),
        current.course_id,
        _read_number("Marks: ", "Marks validation error: enter a number."),
    )
    print(
        "Student updated successfully."
        if database.update_student(updated)
        else "Student not found."
    )


def delete_student(database):
    student_id = _read_integer("Student ID to delete: ", "Student ID must be an integer.")
    if database.delete_student(student_id):
        print("Student deleted successfully.")
    else:
        print("Student not found.")


def delete_course(database):
    course_id = _read_integer("Course ID to delete: ", "Course ID must be an integer.")
    if database.delete_course(course_id):
        print("Course deleted successfully.")
    else:
        print("Course not found.")


def transfer_student_course(database):
    student_id = _read_integer("Student ID to transfer: ", "Student ID must be an integer.")
    new_course_id = _read_integer("New course ID: ", "Course ID must be an integer.")
    history_id = database.transfer_student_course(student_id, new_course_id)
    print(f"Course transfer completed. History ID: {history_id}")


def show_course_history(database):
    student_id_text = input("Student ID (blank for all history): ").strip()
    student_id = (
        None
        if not student_id_text
        else _read_integer_from_text(student_id_text, "Student ID must be an integer.")
    )
    history = database.get_course_history(student_id)
    if not history:
        print("No course transfer history found.")
        return
    print("History ID | Student ID | Student | Old course | New course | Changed at")
    for row in history:
        print(" | ".join(str(value) for value in row))


def _read_integer_from_text(value, error_message):
    try:
        return int(value)
    except ValueError:
        raise ValueError(error_message) from None


def show_course_statistics(database):
    rows = database.get_course_statistics()
    if not rows:
        print("No courses found.")
        return
    print(f"{'Course':<12}{'Students':>10}{'Average':>12}{'Highest':>12}{'Lowest':>12}")
    for course, count, average, highest, lowest in rows:
        print(
            f"{course:<12}{count:>10}"
            f"{('N/A' if average is None else f'{average:.2f}'):>12}"
            f"{('N/A' if highest is None else f'{highest:g}'):>12}"
            f"{('N/A' if lowest is None else f'{lowest:g}'):>12}"
        )


def show_courses_without_students(database):
    courses = database.get_courses_without_students()
    if not courses:
        print("Every course has students.")
        return
    for course in courses:
        print(course.display())


def show_top_students(database):
    count = _read_integer(
        "Number of top students: ", "Number of students must be greater than 0."
    )
    _print_students(database.get_top_students(count))


def show_student_statistics(database):
    total = database.get_total_students()
    average = database.get_average_marks()
    print(f"Total students: {total}")
    print(f"Average marks: {'N/A' if average is None else f'{average:.2f}'}")
    print(f"Total marks: {database.get_total_marks():g}")
    print(f"Highest marks: {database.get_highest_marks()}")
    print(f"Lowest marks: {database.get_lowest_marks()}")


def run_menu(database):
    actions = {
        "1": ("Add Course", add_course),
        "2": ("View Courses", show_courses),
        "3": ("Add Student", add_student),
        "4": ("View All Students (JOIN)", show_students),
        "5": ("Search Student", search_student),
        "6": ("Search Students by Course", search_by_course),
        "7": ("Search Students by Marks", search_by_marks),
        "8": ("Search Students by Name", search_by_name),
        "9": ("Sort Students", sort_students),
        "10": ("Top N Students", show_top_students),
        "11": ("Update Student", update_student),
        "12": ("Delete Student", delete_student),
        "13": ("Delete Course", delete_course),
        "14": ("Student Statistics", show_student_statistics),
        "15": ("Course-wise Statistics", show_course_statistics),
        "16": ("Courses Without Students", show_courses_without_students),
        "17": ("Transfer Student Course", transfer_student_course),
        "18": ("View Course Transfer History", show_course_history),
    }
    while True:
        print("\nStudent Management System — PostgreSQL")
        for choice, (label, _) in actions.items():
            print(f"{choice}. {label}")
        print("19. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "19":
            print("Goodbye.")
            break
        if choice not in actions:
            print("Invalid choice. Enter a number from 1 to 19.")
            continue
        _run_action(database, actions[choice][1])


def main():
    database = Database()
    try:
        database.connect()
        print("Connected to PostgreSQL successfully.")
        database.create_tables()
        run_menu(database)
    except (DatabaseConfigurationError, DatabaseConnectionError) as error:
        print(error)
    except psycopg.Error:
        print("Database operation failed.")
    finally:
        database.close()


if __name__ == "__main__":
    main()
