from typing import List, Optional, Dict
from datetime import datetime, date

from src.backend.user import User
from src.backend.course import Course
from src.utils.data_base_util import DataBaseUtil
from src.backend.exceptions import DuplicationError

# Configure logging
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Student(User):
    changeable_type_fields = {"study_program", "register_number"}

    def __init__(self, user_id: str, username: str, password: str,
                 first_name: str, last_name: str, registered_at: date,
                 remember_me: bool = False, bio: str = None, user_type: str = "student",
                 study_program: str = None, register_number: int = None,
                 active_courses: Optional[List[Course]] = None):
        super().__init__(user_id, username, password, first_name, last_name, registered_at, bio, remember_me, user_type)
        self.study_program = study_program or None
        self.register_number = register_number or None
        self.active_courses = active_courses if active_courses is not None else self._load_courses()

    @classmethod
    def register_new_user(cls, username: str, password: str, first_name: str, last_name: str,
                          study_program: str, register_number: int, remember_me: bool = False) -> str:
        """
        Register a new student user.

        Args:
            username (str): The username for the student.
            password (str): The password for the student.
            first_name (str): The first name of the student.
            last_name (str): The last name of the student.
            study_program (str): The study program the student is enrolled in.
            register_number (int): The unique registration number for the student.
            remember_me (bool): Whether the system should remember the user's session.

        Returns:
            str: The unique user ID assigned to the student.

        Raises:
            DuplicationError: If the username already exists.
        """
        if cls._find_user_by_username(username) is not None:
            raise DuplicationError(f"Registration failed: User '{username}' already exists.")

        user_id = cls._generate_unique_user_id()
        registered_at = datetime.now().date()
        cls._save_user(user_id, username, password, first_name, last_name, registered_at, remember_me, "student")
        cls._save_student(user_id, study_program, register_number)

        logger.info(f"Student registered successfully with username: {username}")
        return user_id

    def register_for_a_course(self, course_id: str):
        """
        Register the student for a specific course.

        Args:
            course_id (str): The unique identifier for the course.

        Raises:
            ValueError: If the course does not exist.
        """
        course = Course.get_course_by_id(course_id)
        if course is None:
            raise ValueError(f"Course with ID '{course_id}' not found.")

        active_course_ids = set()
        if self.active_courses is not None:
            active_course_ids = {course.course_id for course in self.active_courses}
        if course_id in active_course_ids:
            logger.warning(f"Student already registered for course '{course_id}'.")
            return

        if len(course.student_ids) >= course.max_participants:
            logger.warning(f"Course '{course_id}' is full. Registration not allowed.")
            return

        self.active_courses.append(course)

        student_in_course_id = self._generate_unique_user_id()

        db = DataBaseUtil()
        registration_data = {
            "student_in_course_id": student_in_course_id,
            "course_ID": course_id,
            "student_ID": self.user_id
        }
        db.insert_one("student_in_course", registration_data, "student_in_course_id")

        logger.info(f"Successfully registered student '{self.user_id}' for course '{course_id}'.")

    def unregister_for_a_course(self, course_id: str):
        """
        Unregister the student from a specific course.

        Args:
            course_id (str): The unique identifier for the course.

        Logs:
            Warning if the course is not found or the student is not registered for it.
            Info when successfully unregistered.
        """
        course = Course.get_course_by_id(course_id)

        if course is None:
            logger.warning(f"Course with ID '{course_id}' not found.")
            return

        active_course_ids = {course.course_id for course in self.active_courses}
        if course_id not in active_course_ids:
            logger.warning(f"Student '{course_id}' is not registered for course '{course_id}'.")
            return

        for active_course in self.active_courses:
            if active_course.course_id == course_id:
                self.active_courses.remove(active_course)

        db = DataBaseUtil()
        student_in_course_data = db.load_many("student_in_course", "course_ID = %s", [course_id])
        target_record = next((record for record in student_in_course_data if record[2] == self.user_id),
                             None)
        if target_record:
            student_in_course_id = target_record[0]
            db.delete_one("student_in_course", "student_in_course_id", student_in_course_id)
            logger.info(f"Successfully removed student '{self.user_id}' from course '{course_id}'.")
        else:
            logger.warning(f"No registration found for student '{self.user_id}' in course '{course_id}'.")

    def leave_feedback(self, course_id: str, feedback: str, grade: float):
        """
        Allows the student to leave feedback and a grade for a course.

        Args:
            course_id (str): The unique identifier for the course.
            feedback (str): The student's feedback text.
            grade (float): The grade assigned by the student (0.0 to 10.0).

        Raises:
            ValueError: If the grade is not within the allowed range.
        """
        if not any(course.course_id == course_id for course in self.active_courses):
            logger.warning(f"Cannot leave feedback: Student is not registered for course '{course_id}'.")
            return

        if not (0.0 <= grade <= 10.0):
            raise ValueError("Grade must be between 0.0 and 10.0.")

        evaluation_id = self._generate_unique_user_id()
        created_at = datetime.now().isoformat()

        feedback_data = {
            "evaluation_id": evaluation_id,
            "course_id": course_id,
            "author_id": self.user_id,
            "created_at": created_at,
            "feedback": feedback,
            "grade": grade
        }

        db = DataBaseUtil()
        db.insert_one("evaluation", feedback_data, "evaluation_id")

        logger.info(f"Feedback successfully left for course '{course_id}' by student '{self.user_id}'.")

    def search_from_active_courses(self, filters: List[dict]) -> List[Course]:
        """
        Searches for courses in the student's active courses list based on the provided filters.

        Parameters:
            filters (List[dict]): List of dictionaries specifying column filters.

        Returns:
            List[Course]: List of matching Course objects.
        """
        valid_columns = ["course_id", "name", "qualification", "room_id", "schedule", "max_participants"]

        filter_conditions = []
        filter_values = []

        for filter_item in filters:
            for column, allowed_values in filter_item.items():
                if column not in valid_columns:
                    raise ValueError(f"Invalid column name '{column}' in filters.")
                filter_conditions.append(f"{column} IN %s")
                filter_values.append(tuple(allowed_values))

        active_course_ids = [course.course_id for course in self.active_courses]
        if not active_course_ids:
            return []
        filter_conditions.append("course_id IN %s")
        filter_values.append(tuple(active_course_ids))

        db = DataBaseUtil()
        filter_query = " AND ".join(filter_conditions)
        course_data = db.load_many("course", filter_query, filter_values)

        return [Course.get_course_by_id(record["course_id"]) for record in course_data]

    def search_from_new_courses(self, filters: List[dict]) -> List[Course]:
        """
        Searches for courses not in the student's active courses list based on the provided filters.

        Parameters:
            filters (List[dict]): List of dictionaries specifying column filters.

        Returns:
            List[Course]: List of matching Course objects.
        """
        valid_columns = ["course_id", "name", "qualification", "room_id", "schedule", "max_participants"]

        filter_conditions = []
        filter_values = []

        for filter_item in filters:
            for column, allowed_values in filter_item.items():
                if column not in valid_columns:
                    raise ValueError(f"Invalid column name '{column}' in filters.")
                filter_conditions.append(f"{column} IN %s")
                filter_values.append(tuple(allowed_values))

        active_course_ids = [course.course_id for course in self.active_courses]
        if active_course_ids:
            filter_conditions.append("course_id NOT IN %s")
            filter_values.append(tuple(active_course_ids))

        db = DataBaseUtil()
        filter_query = " AND ".join(filter_conditions)
        course_data = db.load_many("course", filter_query, filter_values)
        return [Course.get_course_by_id(record["course_id"]) for record in course_data]

    @classmethod
    def _save_student(cls, user_id: str, study_program: str, register_number: int) -> None:
        student_data = {
            "user_ID": user_id,
            "study_program": study_program,
            "register_number": register_number
        }
        db = DataBaseUtil()
        db.insert_one("student", student_data, "user_ID")

    @staticmethod
    def _find_student_by_user_id(user_id: str) -> Optional[List]:
        db = DataBaseUtil()
        try:
            data = db.load_one("student", "user_ID", user_id)
        except Exception as e:
            data = None
        return data

    def _load_courses(self):
        db = DataBaseUtil()
        student_courses = db.load_many("student_in_course", "student_ID = %s", [self.user_id])
        course_ids = [record[1] for record in student_courses]

        courses = [Course.get_course_by_id(course_id) for course_id in course_ids if Course.get_course_by_id(course_id)]

        logger.info(f"Loaded {len(courses)} active courses for student '{self.user_id}'.")
        return courses

    @classmethod
    def _extend_fields_by_user_id(cls, user_id: str) -> Dict:
        student_data = cls._find_student_by_user_id(user_id)
        if student_data is None:
            logger.warning(f"No student data for user '{user_id}'.")
            return {}

        return {"user_type": "student", "study_program": student_data[1], "register_number": student_data[2]}
