from typing import List, Optional, Dict
from random import randint

from src.backend.user import User
from src.backend.course import Course
from src.utils.data_base_util import DataBaseUtil
from src.backend.qualification import Qualification
from src.backend.exceptions import DuplicationError, WrongTokenError

# Configure logging
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Tutor(User):
    def __init__(self, user_id: str, username: str, password: str,
                 first_name: str, last_name: str,
                 remember_me: bool = False, bio: str = None, user_type: str = "Tutor",
                 qualifications: Optional[List[Qualification]] = None,
                 active_courses: Optional[List["Course"]] = None,
                 evaluations: Optional[List["Evaluation"]] = None):
        super().__init__(user_id, username, password, first_name, last_name, bio, remember_me, user_type)
        self.qualifications = qualifications or []
        self.active_courses = active_courses or []
        self.evaluations = evaluations or []

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
        cls._save_user(user_id, username, password, first_name, last_name, remember_me)
        cls._save_tutor(user_id, qualifications)

        logger.info(f"Tutor registered successfully with username: {username}")
        return user_id

    @classmethod
    def generate_token(cls) -> int:
        existing_tokens = cls._get_tokens()
        while True:
            new_token = randint(100, 999)
            if new_token not in existing_tokens:
                db = DataBaseUtil()
                db.insert_one("tokens", {"token": new_token}, "token")
                return new_token

    @staticmethod
    def _save_tutor(user_id: str, qualifications: List[Qualification]) -> None:
        tutor_data = {
            "user_ID": user_id,
            "qualification": [qualification.name for qualification in qualifications],
        }
        db = DataBaseUtil()
        db.insert_one("tutor", tutor_data, "user_ID")

    @staticmethod
    def _get_tokens() -> set:
        db = DataBaseUtil()
        data = db.load_many("tokens")
        return {item[0] for item in data}

    @staticmethod
    def _remove_token(token: int) -> None:
        db = DataBaseUtil()
        db.delete_one("tokens", "token",token)
        logger.info(f"Registration token '{token}' removed.")

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

        return {"user_type": "Tutor", "qualifications": [Qualification(q) for q in tutor_data[1]],
                "active_courses": Course.get_courses_by_user_id(user_id)}