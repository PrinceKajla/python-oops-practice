class Course:
    def __init__(self, course_id, course_name):
        self.course_id = course_id
        self.course_name = course_name

    def validate(self):
        if self.course_id is not None and (
            isinstance(self.course_id, bool) or not isinstance(self.course_id, int)
        ):
            raise ValueError("Course ID must be an integer.")
        if not isinstance(self.course_name, str) or not self.course_name.strip():
            raise ValueError("Course name cannot be empty.")
        if len(self.course_name.strip()) > 100:
            raise ValueError("Course name must be 100 characters or fewer.")
        return True

    def display(self):
        return f"Course ID: {self.course_id} | Course: {self.course_name.strip()}"
