import sqlite3

from course import Course
from database import Database, DuplicateCourseError, DuplicateStudentError
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
        _read_integer("Course ID: ", "Course ID must be an integer."),
        _read_number("Marks: ", "Marks validation error: enter a number."),
    )


def _print_students(students):
    if not students:
        print("No students found.")
        return
    for student in students:
        print(student.display())


def add_course(database):
    try:
        course_id = _read_integer("Course ID: ", "Course ID must be an integer.")
        course_name = input("Course name: ")
        database.add_course(Course(course_id, course_name))
        print("Course added successfully.")
    except (DuplicateCourseError, ValueError) as error:
        print(error)
    except sqlite3.Error:
        print("Database operation failed.")


def show_courses(database):
    try:
        courses = database.get_all_courses()
        if not courses:
            print("No courses found.")
            return
        for course in courses:
            print(course.display())
    except sqlite3.Error:
        print("Database operation failed.")


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
        rows = database.get_students_with_courses()
        if not rows:
            print("No students found.")
            return
        for student_id, name, course_name, marks in rows:
            print(
                f"ID: {student_id} | Name: {name} | Course: {course_name} "
                f"| Marks: {marks:g}"
            )
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
    try:
        course_name = input("Course name: ")
        _print_students(database.get_students_by_course(course_name))
    except ValueError as error:
        print(error)
    except sqlite3.Error:
        print("Database operation failed.")


def search_by_marks(database):
    try:
        min_marks = _read_number("Minimum marks (0-100): ", "Invalid marks.")
        _print_students(database.get_students_by_marks(min_marks))
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


def sort_students(database):
    print("Sort by: 1. Marks highest first  2. Marks lowest first  3. Name")
    choice = input("Choose a sort order: ").strip()
    try:
        if choice == "1":
            _print_students(database.get_students_sorted_by_marks(desc=True))
        elif choice == "2":
            _print_students(database.get_students_sorted_by_marks(desc=False))
        elif choice == "3":
            _print_students(database.get_students_sorted_by_name())
        else:
            print("Invalid sorting option.")
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
        current = database.get_student_by_id(student_id)
        if current is None:
            print("Student not found.")
            return
        print("Current student:")
        print(current.display())
        updated_student = Student(
            student_id,
            input("Name: "),
            _read_integer("Age: ", "Age validation error: enter an integer."),
            current.course_id,
            _read_number("Marks: ", "Marks validation error: enter a number."),
        )
        rowcount = database.update_student(updated_student)
        print("Student updated successfully." if rowcount else "Student not found.")
        print("Use option 15 to transfer the student to another course.")
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
        print(f"Total Students      : {database.get_total_students()}")
        total_marks = database.get_total_marks()
        average = database.get_average_marks()
        highest = database.get_highest_marks()
        lowest = database.get_lowest_marks()
        print(f"Total Marks         : {total_marks:g}")
        print("Average Marks       : " + ("N/A" if average is None else f"{average:.2f}"))
        print("Highest Marks       : " + ("N/A" if highest is None else f"{highest:g}"))
        print("Lowest Marks        : " + ("N/A" if lowest is None else f"{lowest:g}"))
    except sqlite3.Error:
        print("Database operation failed.")


def show_course_statistics(database):
    try:
        statistics = database.get_course_statistics()
        if not statistics:
            print("No courses found.")
            return
        print(f"{'Course':<12}{'Students':>10}{'Average':>12}{'Highest':>12}{'Lowest':>12}")
        print("----------------------------------------------------------")
        for course, count, average, highest, lowest in statistics:
            average_text = "N/A" if average is None else f"{average:.2f}"
            highest_text = "N/A" if highest is None else f"{highest:g}"
            lowest_text = "N/A" if lowest is None else f"{lowest:g}"
            print(
                f"{course:<12}{count:>10}{average_text:>12}"
                f"{highest_text:>12}{lowest_text:>12}"
            )
    except sqlite3.Error:
        print("Database operation failed.")


def show_courses_without_students(database):
    try:
        courses = database.get_courses_without_students()
        if not courses:
            print("Every course has students.")
            return
        print("Courses without students:")
        for course in courses:
            print(course.display())
    except sqlite3.Error:
        print("Database operation failed.")


def transfer_student_course(database):
    try:
        student_id = _read_integer(
            "Student ID to transfer: ", "Student ID must be an integer."
        )
        student = database.get_student_by_id(student_id)
        if student is None:
            print("Student not found.")
            return
        print(f"Current course: {student.course_name} (ID {student.course_id})")
        new_course_id = _read_integer(
            "New course ID: ", "Course ID must be an integer."
        )
        new_course = database.get_course_by_id(new_course_id)
        if new_course is None:
            print("Invalid course ID.")
            return
        history_id = database.transfer_student_course(student_id, new_course_id)
        print(
            f"Course transfer completed: {student.course_name} -> "
            f"{new_course.course_name}. History ID: {history_id}"
        )
    except ValueError as error:
        print(error)
    except sqlite3.Error:
        print("Database operation failed; the transfer was rolled back.")


def show_course_history(database):
    try:
        student_id_text = input("Student ID (blank for all history): ").strip()
        if student_id_text:
            try:
                student_id = int(student_id_text)
            except ValueError:
                raise ValueError("Student ID must be an integer.") from None
            history = database.get_student_course_history(student_id)
        else:
            history = database.get_course_history()
        if not history:
            print("No course transfer history found.")
            return
        print("History ID | Student ID | Student | Old course | New course | Changed at")
        for history_id, history_student_id, name, old_course, new_course, changed_at in history:
            print(
                f"{history_id} | {history_student_id} | {name} | {old_course} "
                f"| {new_course} | {changed_at}"
            )
    except ValueError:
        print("Student ID must be an integer.")
    except sqlite3.Error:
        print("Database operation failed.")


def run_menu(database):
    while True:
        print("\nStudent Management System")
        print("1. Add Course")
        print("2. View Courses")
        print("3. Add Student")
        print("4. View All Students")
        print("5. Search Student")
        print("6. Search Students by Course")
        print("7. Search Students by Marks")
        print("8. Sort Students")
        print("9. Top N Students")
        print("10. Update Student")
        print("11. Delete Student")
        print("12. Student Statistics")
        print("13. Course-wise Statistics")
        print("14. Courses Without Students")
        print("15. Transfer Student Course")
        print("16. View Course Transfer History")
        print("17. Exit")

        choice = input("Choose an option: ").strip()
        if choice == "1":
            add_course(database)
        elif choice == "2":
            show_courses(database)
        elif choice == "3":
            add_student(database)
        elif choice == "4":
            show_students(database)
        elif choice == "5":
            search_student(database)
        elif choice == "6":
            search_by_course(database)
        elif choice == "7":
            search_by_marks(database)
        elif choice == "8":
            sort_students(database)
        elif choice == "9":
            show_top_students(database)
        elif choice == "10":
            update_student(database)
        elif choice == "11":
            delete_student(database)
        elif choice == "12":
            show_student_statistics(database)
        elif choice == "13":
            show_course_statistics(database)
        elif choice == "14":
            show_courses_without_students(database)
        elif choice == "15":
            transfer_student_course(database)
        elif choice == "16":
            show_course_history(database)
        elif choice == "17":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Enter a number from 1 to 17.")


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
