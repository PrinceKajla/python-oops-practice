class Student:
    def __init__(self, student_id, name, age, course_id, marks, course_name=None):
        if isinstance(student_id, bool) or not isinstance(student_id, int):
            raise ValueError("Student ID must be an integer.")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Student name cannot be empty.")
        if isinstance(age, bool) or not isinstance(age, int) or age <= 0:
            raise ValueError("Age validation error: age must be an integer greater than 0.")
        if isinstance(course_id, bool) or not isinstance(course_id, int):
            raise ValueError("Course ID must be an integer.")
        if isinstance(marks, bool) or not isinstance(marks, (int, float)):
            raise ValueError("Marks validation error: marks must be between 0 and 100.")
        if not 0 <= marks <= 100:
            raise ValueError("Marks validation error: marks must be between 0 and 100.")
        if course_name is not None and (not isinstance(course_name, str) or not course_name.strip()):
            raise ValueError("Course name cannot be empty.")

        self.student_id = student_id
        self.name = name.strip()
        self.age = age
        self.course_id = course_id
        self.marks = float(marks)
        self.course_name = course_name.strip() if course_name is not None else None

    def display(self):
        course = self.course_name or f"Course ID {self.course_id}"
        return (
            f"ID: {self.student_id} | Name: {self.name} | Age: {self.age} | "
            f"Course: {course} | Marks: {self.marks:g}"
        )
