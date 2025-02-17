from typing import List, Optional, Dict
from random import randint
from datetime import datetime, date

from src.backend.user import User
from src.backend.course import Course
from src.backend.evaluation import Evaluation
from src.utils.data_base_util import DataBaseUtil
from src.backend.qualification import Qualification
from src.backend.exceptions import DuplicationError, WrongTokenError

# Configure logging
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Tutor(User):
    changeable_type_fields = {"qualification"}

    def __init__(self, user_id: str, username: str, password: str,
                 first_name: str, last_name: str, registered_at: date,
                 remember_me: bool = False, bio: str = None, user_type: str = "tutor",
                 qualifications: Optional[List[Qualification]] = None):
        super().__init__(user_id, username, password, first_name, last_name, registered_at, bio, remember_me, user_type)
        self.qualifications = qualifications or []

    @classmethod
    def register_new_user(cls, username: str, password: str, first_name: str, last_name: str,
                          token: int, qualifications: List[Qualification], remember_me: bool = False) -> str:
        """
        Registers a new tutor with validation.

        Args:
            username (str): The tutor's username.
            password (str): The tutor's password.
            first_name (str): The tutor's first name.
            last_name (str): The tutor's last name.
            token (int): The unique registration token for the tutor.
            qualifications (List[Qualification]): List of the tutor's qualifications.
            remember_me (bool): The tutor's remember me option.

        Returns:
            str: The newly registered tutor's user ID.

        Raises:
            DuplicationError: If a tutor with the username already exists.
            WrongTokenError: If the tutor register token is invalid.
        """
        if cls._find_user_by_username(username) is not None:
                raise DuplicationError(f"Registration failed: User '{username}' already exists.")

        if token not in cls._get_tokens():
            raise WrongTokenError(f"Registration failed: Invalid register token '{token}'.")
        cls._remove_token(token)

        user_id = cls._generate_unique_user_id()
        registered_at = datetime.now().date()
        cls._save_user(user_id, username, password, first_name, last_name, registered_at, remember_me, "tutor")
        cls._save_tutor(user_id, qualifications)

        logger.info(f"Tutor registered successfully with username: {username}")
        return user_id

    @property
    def evaluations(self) -> List[Evaluation]:
        course_ids = [course.course_id for course in Course.get_courses_by_user_id(self.user_id)]
        return Evaluation.get_evaluations_by_course_ids(course_ids)

    @property
    def active_courses(self) -> List[Course]:
        return Course.get_courses_by_user_id(self.user_id)

    @classmethod
    def _save_tutor(cls, user_id: str, qualifications: List[Qualification]) -> None:
        tutor_data = {
            "user_ID": user_id,
            "qualification": qualifications,
        }
        tutor_data = cls._prepare_for_jsonb(tutor_data)
        db = DataBaseUtil()
        db.insert_one("tutor", tutor_data, "user_ID")

    @staticmethod
    def _find_tutor_by_user_id(user_id: str) -> Optional[List]:
        db = DataBaseUtil()
        try:
            data = db.load_one("tutor", "user_ID", user_id)
        except Exception as e:
            data = None
        return data

    @classmethod
    def _extend_fields_by_user_id(cls, user_id: str) -> Dict:
        tutor_data = cls._find_tutor_by_user_id(user_id)
        if tutor_data is None:
            logger.warning(f"No tutor data for user '{user_id}'.")
            return {}

        return {"qualifications": [Qualification(q) for q in tutor_data[1]]}
