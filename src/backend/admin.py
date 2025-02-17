from typing import List, Optional, Dict
from datetime import datetime, date

from src.backend.user import User
from src.backend.course import Course
from src.utils.data_base_util import DataBaseUtil
from src.backend.exceptions import DuplicationError, WrongTokenError

# Configure logging
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Admin(User):
    changeable_type_fields = {"role"}

    def __init__(self, user_id: str, username: str, password: str,
                 first_name: str, last_name: str, registered_at: date,
                 remember_me: bool = False, bio: str = None, user_type: str = "admin",
                 role: str = None):
        super().__init__(user_id, username, password, first_name, last_name, registered_at, bio, remember_me, user_type)
        self.role = role or None

    @classmethod
    def register_new_user(cls, username: str, password: str, first_name: str, last_name: str,
                          role: str, token: int, remember_me: bool = False) -> str:
        """
        Registers a new admin user.

        Args:
            username (str): The username of the new user.
            password (str): The password for the new user.
            first_name (str): The first name of the new user.
            last_name (str): The last name of the new user.
            role (str): The role assigned to the admin.
            remember_me (bool, optional): Whether to remember the user session (default is False).

        Returns:
            str: The unique user ID of the newly registered admin.

        Raises:
            DuplicationError: If the username is already taken.
        """
        if cls._find_user_by_username(username) is not None:
            raise DuplicationError(f"Registration failed: User '{username}' already exists.")

        if token not in cls._get_tokens():
            raise WrongTokenError(f"Registration failed: Invalid register token '{token}'.")
        cls._remove_token(token)

        user_id = cls._generate_unique_user_id()
        registered_at = datetime.now().date()
        cls._save_user(user_id, username, password, first_name, last_name, registered_at, remember_me, "admin")
        cls._save_admin(user_id, role)

        logger.info(f"Admin registered successfully with username: {username}")
        return user_id

    @classmethod
    def banish_user(cls, user_id: str):
        """
        Banishes (deletes) a user from the system and removes their associated data.

        Args:
            user_id (str): The user ID of the user to be banned.
        """
        if cls.get_user_by_id(user_id) is None:
            logger.warning(f"User '{user_id}' not found.")
            raise ValueError(f"User '{user_id}' not found.")

        db = DataBaseUtil()
        db.delete_many("student_in_course", "student_id", [user_id])
        db.delete_many("course", "user_id", [user_id])
        db.delete_many("student", "user_id", [user_id])
        db.delete_many("tutor", "user_id", [user_id])
        db.delete_many("users", "user_id", [user_id])
        logger.info(f"User with ID '{user_id}' deleted successfully.")

    @classmethod
    def search_for_user(cls, username_starts_with_part: str) -> List[User]:
        """
        Searches for users whose username starts with a specified prefix.

        Args:
            username_starts_with_part (str): The prefix of the username to search for.

        Returns:
            List[User]: A list of User objects that match the search criteria.

        Raises:
            ValueError: If the search string is empty.
        """
        if not username_starts_with_part:
            raise ValueError("The search string cannot be empty.")

        search_value = f"{username_starts_with_part}%"

        db = DataBaseUtil()
        results = db.load_many("users", "username LIKE %s", [search_value])

        users = [User.get_user_by_id(record[0]) for record in results]
        return users

    @classmethod
    def find_courses_at_some_time(cls, schedule: str) -> List[Course]:
        """
        Finds courses scheduled at a specific time on a given day.

        Parameters:
            schedule (str): A string representing the day and hour in the format "Day Hour", e.g., "Mon 10".

        Returns:
            List[Course]: A list of Course objects that match the day and time criteria.

        Raises:
            ValueError: If the schedule format is invalid or the time is not an integer.
        """
        if not isinstance(schedule, str) or len(schedule.split()) != 2:
            raise ValueError("Schedule format must be 'Day Hour' e.g. 'Mon 10'")
        day, time_str = schedule.split()
        try:
            hour = int(time_str)
        except ValueError:
            raise ValueError("Time must be an integer representing the hour.")

        day_filter = f"{day}%"

        db = DataBaseUtil()
        results = db.load_many("course", "schedule LIKE %s", [day_filter])

        matching_courses = []
        for course in results:
            course_schedule = course[5]
            try:
                course_day, course_time = course_schedule.split(' ', 1)
                start_time, end_time = course_time.split('-')
                start_hour = int(start_time)
                end_hour = int(end_time)

                if start_hour <= hour <= end_hour:
                    matching_courses.append(Course.get_course_by_id(course[0]))
            except ValueError:
                continue

        return matching_courses

    @classmethod
    def add_token(cls, token: int):
        """
        Adds a token to the database if it does not already exist.

        Args:
            token (int): The token to be added.
        """
        existing_tokens = cls._get_tokens()
        if token not in existing_tokens:
            db = DataBaseUtil()
            db.insert_one("tokens", {"token": token}, "token")

    @classmethod
    def _save_admin(cls, user_id: str, role: str) -> None:
        admin_data = {
            "user_ID": user_id,
            "role": role
        }
        db = DataBaseUtil()
        db.insert_one("admin", admin_data, "user_ID")

    @staticmethod
    def _find_admin_by_user_id(user_id: str) -> Optional[List]:
        db = DataBaseUtil()
        try:
            data = db.load_one("admin", "user_ID", user_id)
        except Exception as e:
            data = None
        return data

    @classmethod
    def _extend_fields_by_user_id(cls, user_id: str) -> Dict:
        admin_data = cls._find_admin_by_user_id(user_id)
        if admin_data is None:
            logger.warning(f"No admin data for user '{user_id}'.")
            return {}

        return {"user_type": "admin", "role": admin_data[1]}
