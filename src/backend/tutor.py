from src.backend.data_base_util import (find_user_by_username, save_user, register_token_exists,
                                        remove_register_token, save_tutor, get_tutor_ids)

from src.backend.user import User
from src.utils.password_utils import PasswordUtils
from src.backend.course import Course
from src.backend.evaluation import Evaluation
from src.backend.time_window import TimeWindow
from src.backend.qualification import Qualification
from src.backend.exceptions import DuplicationError, WrongTokenError

from typing import List, Optional

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Tutor(User):
    # TODO attributes based on the issue and JSON data base structure, might change later
    def __init__(self, user_id: str, username: str, password: str,
                 tutor_id: str, first_name: str, last_name: str,
                 remember_me: bool = False, bio: str = None,
                 qualifications: Optional[List["Qualification"]] = None,
                 available_time: Optional[List["TimeWindow"]] = None,
                 active_courses: Optional[List["Course"]] = None,
                 evaluation: Optional["Evaluation"] = None):
        super().__init__(user_id, username, password, first_name, last_name, remember_me, bio)
        self.tutor_id = tutor_id
        self.qualifications = qualifications or []
        self.available_time = available_time or []
        self.active_courses = active_courses or []
        self.evaluation = evaluation

    @staticmethod
    def register_new_tutor(username: str, first_name: str, last_name: str, password: str,
                          tutor_register_number: int, qualifications: List["Qualification"]) -> str:
        """
        Register a new tutor with validation and default settings.
        """
        if find_user_by_username(username):
            raise DuplicationError(f"User with username '{username}' already exists.")

        if not register_token_exists(tutor_register_number):
            raise WrongTokenError(f"Invalid register token '{tutor_register_number}'.")
        remove_register_token(tutor_register_number)

        available_time = Tutor._default_available_time()
        evaluation = Evaluation()

        user_id = User._generate_unique_user_id()
        user_data = {
            "userID": user_id,
            "username": username,
            "password": PasswordUtils.hash_password(password),
            "remember_me": False,
            "bio": None,
            "first_name": first_name,
            "last_name": last_name
        }

        tutor_data = {
            "userID": user_id,
            "tutorID": User._generate_unique_user_id(),
            "qualifications": qualifications,
            "available_time": available_time,
            "active_courses": None,
            "evaluation": evaluation
        }

        save_user(user_data)
        save_tutor(tutor_data)

        logger.info(f"Tutor registered successfully with username: {username}")
        return user_id

    @staticmethod
    def _default_available_time() -> List[TimeWindow]:
        """
        Generate default available time for a tutor.
        """
        return [TimeWindow(day, "9:00", "18:00")
                for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]]

    @classmethod
    def get_ids(cls) -> set:
        """
        Retrieves all tutor IDs.
        """
        return set(get_tutor_ids())
