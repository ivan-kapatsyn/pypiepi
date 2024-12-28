# TODO data_base_util Dummy
from src.backend.data_base_util import find_user_by_username, save_user, users_with_remember_me, get_user_ids, \
    find_user_by_id, register_token_exists, remove_register_token, save_tutor, get_tutor_ids

from src.utils.password_utils import PasswordUtils
from src.backend.course import Course
from src.backend.evaluation import Evaluation
from src.backend.time_window import TimeWindow
from src.backend.qualification import Qualification
from src.backend.exceptions import DuplicationError, WrongTokenError

from typing import List, Optional, Literal
from secrets import token_hex
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class User:
    def __init__(self, user_id: str, username: str, password: str, remember_me: bool = False, bio: str = None,
                 first_name: str = None, last_name: str = None):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.remember_me = remember_me
        # TODO replace with Student/Tutor info
        self.bio = bio
        self.first_name = first_name
        self.last_name = last_name

    @classmethod
    def authenticate(cls, username: str, password: str) -> Optional["User"]:
        """
        Authenticate a user by username and password.
        Returns:
            User instance if successful, None otherwise.
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
            bio=user_data.get("bio", None),
            first_name=user_data.get("first_name", None),
            last_name=user_data.get("last_name", None),
        )

    @classmethod
    def register_new_user(cls, username: str, password: str, remember_me: bool = False) -> "User":
        """
        Registers a new user.
        Raises:
            DuplicationError: If the username already exists.
        Returns:
            User instance of the new user.
        """
        if find_user_by_username(username):
            raise DuplicationError(f"User with username '{username}' already exists.")

        hashed_password = PasswordUtils.hash_password(password)
        user_id = cls._generate_unique_user_id("user")

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
                    remember_me=user.get("remember_me", False), bio=user.get("bio", None),
                    first_name=user.get("first_name", None), last_name=user.get("last_name", None))
                for user in matching_users]

    @staticmethod
    def _generate_unique_user_id(user_type: Literal["user", "tutor"]) -> str:
        """
        Returns a random 16-character string
        """
        user_ids = []
        if user_type == "user":
            user_ids = set(get_user_ids())
        elif user_type == "tutor":
            user_ids = set(get_tutor_ids())

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
            bio=user.get("bio", None),
            first_name=user.get("first_name", None),
            last_name=user.get("last_name", None)
        )

class Tutor(User):
    # TODO attributes based on the issue and JSON data base structure, might change later
    def __init__(self, user_id: str, username: str, password: str,
                 tutor_id: str, first_name: str, last_name: str,
                 remember_me: bool = False, bio: str = None,
                 qualifications: Optional[List["Qualification"]] = None,
                 available_time: Optional[List["TimeWindow"]] = None,
                 active_courses: Optional[List["Course"]] = None,
                 evaluation: Optional["Evaluation"] = None):
        super().__init__(user_id, username, password, remember_me, bio, first_name, last_name)
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

        user_id = User._generate_unique_user_id("user")
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
            "tutorID": User._generate_unique_user_id("tutor"),
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

class Student(User):
    pass
