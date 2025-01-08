from typing import List, Optional, Dict

from src.backend.user import User
from src.utils.data_base_util import DataBaseUtil
from src.utils.password_utils import PasswordUtils
from src.backend.course import Course
from src.backend.evaluation import Evaluation
from src.backend.qualification import Qualification
from src.backend.exceptions import DuplicationError, WrongTokenError

# Configure logging
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Tutor(User):
    def __init__(self, user_id: str, username: str, password: str,
                 first_name: str, last_name: str, tutor_id: str,
                 remember_me: bool = False, bio: str = None,
                 qualifications: Optional[List[Qualification]] = None,
                 active_courses: Optional[List[Course]] = None,
                 evaluation: Optional[Evaluation] = None):
        super().__init__(user_id, username, password, first_name, last_name, bio, remember_me)
        self.tutor_id = tutor_id
        self.qualifications = qualifications or []
        self.active_courses = active_courses or []
        self.evaluation = evaluation or Evaluation()

    @classmethod
    def register_new_tutor(cls, username: str, password: str, first_name: str, last_name: str,
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
        hashed_password = PasswordUtils.hash_password(password)
        cls._save_user(user_id, username, hashed_password, first_name, last_name, remember_me)

        tutor_id = cls._generate_unique_user_id()
        cls._save_tutor(tutor_id, user_id, qualifications)

        logger.info(f"Tutor registered successfully with username: {username}")
        return user_id

    @classmethod
    def _get_ids(cls) -> set:
        db = DataBaseUtil()
        data = {tutor[0] for tutor in db.load_many("tutor")}
        db.__del__()
        return data

    @staticmethod
    def _save_tutor(tutor_id: str, user_id: str, qualifications: List[Qualification]) -> None:
        tutor_data = {
            "tutor_ID": tutor_id,
            "user_ID": user_id,
            "qualification": qualifications
        }
        db = DataBaseUtil()
        db.insert_one("tutor", tutor_data, "tutor_ID")
        db.__del__()

    @staticmethod
    def _get_tokens() -> set:
        db = DataBaseUtil()
        data = db.load_many("tokens")
        db.__del__()
        return {item[0] for item in data}

    @staticmethod
    def _remove_token(token: int) -> None:
        db = DataBaseUtil()
        db.delete_one("tokens", token)
        logger.info(f"Registration token '{token}' removed.")
        db.__del__()

    @staticmethod
    def _find_tutor_by_user_id(user_id: str) -> Optional[List]:
        db = DataBaseUtil()
        try:
            data = db.load_data("tutor", "user_ID", user_id)
        except Exception as e:
            data = None
        finally:
            db.__del__()
        return data

    @classmethod
    def _extend_fields_by_user_id(cls, user_id: str) -> Dict:
        tutor_data = cls._find_tutor_by_user_id(user_id)
        if tutor_data is None:
            logger.warning(f"No tutor data for user '{user_id}'.")
            return {}

        return {"tutor_id": tutor_data[0], "qualifications": [Qualification(q) for q in tutor_data[2]]}
