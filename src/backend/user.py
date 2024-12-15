# TODO data_base_util Dummy
from src.backend.data_base_util import find_user_by_username, save_user, users_with_remember_me, get_user_ids, \
    find_user_by_id, add_course_to_tutor, add_student_to_course

from src.utils.password_utils import PasswordUtils
from typing import List, Optional, Union
from secrets import token_hex
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# TODO put later elsewhere
class DuplicationError(Exception):
    pass


class User:
    def __init__(self, user_id: str, username: str, password: str, remember_me: bool = False, bio: str = None):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.remember_me = remember_me
        # TODO replace with Student/Tutor info
        self.bio = bio

    @classmethod
    def authenticate(cls, username: str, password: str) -> Optional["User"]:
        """
        Returns a user instance if authentication is successful, None otherwise.
        """
        user_data = find_user_by_username(username)
        if not user_data or not PasswordUtils.verify_password(password, user_data["password"]):
            logger.warning(f"Authentication failed for username: {username}")
            return None

        return cls(
            user_id=user_data["userID"],
            username=user_data["username"],
            password=user_data["password"],
            remember_me=user_data.get("remember_me", False),
            bio=user_data.get("bio")
        )

    @classmethod
    def register_new_user(cls, username: str, password: str, remember_me: bool = False) -> "User":
            """
            Raises DuplicationError if a user with the same username already exists.
            Returns an instance of the created User.
            """
            if find_user_by_username(username):
                raise DuplicationError(f"User with username '{username}' already exists.")

            hashed_password = PasswordUtils.hash_password(password)
            user_id = cls._generate_unique_user_id()

            new_user_data = {
                "userID": user_id,
                "username": username,
                "password": hashed_password,
                "remember_me": remember_me
            }

            save_user(new_user_data)
            logger.info(f"User registered successfully with username: {username}")

            return cls(
                user_id=user_id,
                username=username,
                password=hashed_password,
                remember_me=remember_me,
            )

    @classmethod
    def search_for_a_saved_users(cls, username_substr: str) -> List["User"]:
        """
        Returns a list of matching User instances.
        """
        users_data = users_with_remember_me()

        # TODO remake on the data base side
        matching_users = [user for user in users_data if user['username'].startswith(username_substr.lower())]

        return [cls(user_id=user["userID"], username=user["username"], password=user["password"],
                    remember_me=user.get("remember_me", False), bio=user.get("bio"))
                for user in matching_users]

    @staticmethod
    def _generate_unique_user_id() -> str:
        """
        Returns a random 16-character string
        """
        user_ids = get_user_ids()
        while True:
            user_id = token_hex(8)
            if user_id not in user_ids:
                return user_id

    @classmethod
    def get_user_by_id(cls, user_id: str) -> Optional["User"]:
        """
        Retrieve a user by their ID.
        """
        # TODO remake it to retrieve a User instance by its id in the db
        user = find_user_by_id(user_id)
        if not user:
            return None
        return cls(
            user_id=user["userID"],
            username=user["username"],
            password=user["password"],
            remember_me=user.get("remember_me", False),
            bio=user.get("bio")
        )

class Qualification:
    def __init__(self, name: str):
        self.name = name

class TimeWindow:
    def __init__(self, day: str, start_time: str, end_time: str):
        self.day = day
        self.start_time = start_time
        self.end_time = end_time

class Evaluation:
    def __init__(self, ratings: Optional[List[int]] = None):
        self.ratings = ratings or []

class Room:
    def __init__(self, name: str):
        self.name = name

class Tutor(User):
    # TODO attributes based on the issue and JSON data base structure, might change later
    def __init__(self, user_id: str, username: str, password: str,
                 tutor_id: str, first_name: str, last_name: str,
                 remember_me: bool = False, bio: str = None,
                 qualifications: Optional[List["Qualification"]] = None,
                 available_time: Optional[List["TimeWindow"]] = None,
                 active_courses: Optional[List["Course"]] = None,
                 evaluation: Optional["Evaluation"] = None):
        super().__init__(user_id, username, password, remember_me, bio)
        self.tutor_id = tutor_id
        self.first_name = first_name
        self.last_name = last_name
        self.qualifications = qualifications or []
        self.available_time = available_time or []
        self.active_courses = active_courses or []
        self.evaluation = evaluation

    def add_course(self, course: "Course"):
        """
        Add a new course to the tutor's active courses.
        """
        if course in self.active_courses:
            logger.warning(f"Course '{course.name}' is already assigned to tutor '{self.username}'.")
            return
        add_course_to_tutor(self, course)
        self.active_courses.append(course)
        logger.info(f"Course '{course.name}' added to tutor '{self.username}'.")


class Student(User):
    pass


class Course:
    def __init__(self, name: str, qualification: "Qualification", max_participants: int, tutor: Tutor,
                 students: Optional[List["Student"]] = None,
                 schedule: Optional[List["TimeWindow"]] = None,
                 location: Optional[Union["Room", List["Room"]]] = None,
                 evaluation: Optional["Evaluation"] = None,
                 announcements: Optional[List[str]] = None):
        self.name = name
        self.qualification = qualification
        self.max_participants = max_participants
        self.tutor = tutor
        self.students = students or []
        self.schedule = schedule or []
        self.location = location
        self.evaluation = evaluation
        self.announcements = announcements or []

    def add_student(self, student: "Student"):
        """
        Add a student to the course, ensuring the maximum limit isn't exceeded.
        """
        if len(self.students) >= self.max_participants:
            logger.warning(f"Cannot add student: Maximum participants ({self.max_participants}) reached.")
            return
        add_student_to_course(student, self)
        self.students.append(student)
        logger.info(f"Student '{student}' added to course '{self.name}'.")