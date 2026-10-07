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


def _print_students(students):
    if not students:
        print("No students found.")
        return
    for student in students:
        print(student.display())


def add_student(database):
    try:
        student_id = _read_integer("Student ID: ", "Student ID must be an integer.")
        database.add_student(_read_student_details(student_id))
        print("Student added successfully.")
    except (DuplicateStudentError, ValueError) as error:
        print(error)
    except sqlite3.Error:
        print("Database operation failed.")


def show_students(database):
    try:
        _print_students(database.get_all_students())
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


def search_by_course(database):
    print("Course search options: 1. Exact course  2. Course AND minimum marks")
    print("3. Either of two courses (OR)")
    try:
        mode = input("Choose a course search: ").strip()
        if mode == "1":
            course = input("Course: ")
            students = database.get_students_by_course(course)
        elif mode == "2":
            course = input("Course: ")
            min_marks = _read_number(
                "Minimum marks (0-100): ", "Invalid marks."
            )
            students = database.get_students_by_course_and_marks(course, min_marks)
        elif mode == "3":
            first_course = input("First course: ")
            second_course = input("Second course: ")
            students = database.get_students_by_either_course(
                first_course, second_course
            )
        else:
            print("Invalid course search option.")
            return
        _print_students(students)
    except ValueError as error:
        print(error)
    except sqlite3.Error:
        print("Database operation failed.")


def search_by_name(database):
    try:
        keyword = input("Name keyword: ")
        _print_students(database.search_students_by_name(keyword))
    except ValueError as error:
        print(error)
    except sqlite3.Error:
        print("Database operation failed.")


def filter_by_marks(database):
    try:
        min_marks = _read_number("Minimum marks (0-100): ", "Invalid marks.")
        _print_students(database.get_students_by_marks(min_marks))
    except ValueError as error:
        print(error)
    except sqlite3.Error:
        print("Database operation failed.")


def sort_by_marks(database):
    choice = input("Sort marks: 1. Highest first  2. Lowest first: ").strip()
    if choice not in ("1", "2"):
        print("Invalid sorting option.")
        return
    try:
        _print_students(database.get_students_sorted_by_marks(desc=choice == "1"))
    except sqlite3.Error:
        print("Database operation failed.")


def show_top_students(database):
    try:
        limit = _read_integer(
            "Number of top students: ",
            "Number of students must be greater than 0.",
        )
        _print_students(database.get_top_students(limit))
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
        rowcount = database.update_student(_read_student_details(student_id))
        print("Student updated successfully." if rowcount else "Student not found.")
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

        if database.delete_student(student_id):
            print("Student deleted successfully.")
        else:
            print("Student not found.")
    except ValueError as error:
        print(error)
    except sqlite3.Error:
        print("Database operation failed.")


def show_student_statistics(database):
    try:
        total_students = database.get_total_students()
        total_marks = database.get_total_marks()
        average_marks = database.get_average_marks()
        highest_marks = database.get_highest_marks()
        lowest_marks = database.get_lowest_marks()

        print(f"Total Students      : {total_students}")
        print(f"Total Marks         : {total_marks:g}")
        average_display = "N/A" if average_marks is None else f"{average_marks:.2f}"
        highest_display = "N/A" if highest_marks is None else f"{highest_marks:g}"
        lowest_display = "N/A" if lowest_marks is None else f"{lowest_marks:g}"
        print(f"Average Marks       : {average_display}")
        print(f"Highest Marks       : {highest_display}")
        print(f"Lowest Marks        : {lowest_display}")
    except sqlite3.Error:
        print("Database operation failed.")


def show_course_statistics(database):
    try:
        statistics = database.get_course_statistics()
        if not statistics:
            print("No course statistics available.")
        else:
            print(f"{'Course':<12}{'Students':>10}{'Average':>12}{'Highest':>12}{'Lowest':>12}")
            print("----------------------------------------------------------")
            for course, total_students, average, highest, lowest in statistics:
                print(
                    f"{course:<12}{total_students:>10}{average:>12.2f}"
                    f"{highest:>12g}{lowest:>12g}"
                )

        min_average = 80
        qualifying_courses = database.get_courses_above_average(min_average)
        print(f"\nCourses with average marks >= {min_average}:")
        if not qualifying_courses:
            print("No courses meet this average.")
        else:
            for course, average in qualifying_courses:
                print(f"{course}: {average:.2f}")
    except sqlite3.Error:
        print("Database operation failed.")


def run_menu(database):
    while True:
        print("\nStudent Management System")
        print("1. Add Student")
        print("2. View All Students")
        print("3. Search Student by ID")
        print("4. Search Student by Course")
        print("5. Search Student by Name")
        print("6. Filter Students by Marks")
        print("7. Sort Students by Marks")
        print("8. Top N Students")
        print("9. Update Student")
        print("10. Delete Student")
        print("11. Student Statistics")
        print("12. Course-wise Statistics")
        print("13. Exit")

        choice = input("Choose an option: ").strip()
        if choice == "1":
            add_student(database)
        elif choice == "2":
            show_students(database)
        elif choice == "3":
            search_student(database)
        elif choice == "4":
            search_by_course(database)
        elif choice == "5":
            search_by_name(database)
        elif choice == "6":
            filter_by_marks(database)
        elif choice == "7":
            sort_by_marks(database)
        elif choice == "8":
            show_top_students(database)
        elif choice == "9":
            update_student(database)
        elif choice == "10":
            delete_student(database)
        elif choice == "11":
            show_student_statistics(database)
        elif choice == "12":
            show_course_statistics(database)
        elif choice == "13":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Enter a number from 1 to 13.")


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
