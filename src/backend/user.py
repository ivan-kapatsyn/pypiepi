""" User Passwords
arthur.morgan: password123
john.doe: newpassword
jane.doe: mypassword
john.marston: mypasswordisbetter
mary.stuart: stupidpassword
"""
from typing import List, Optional, Dict, Any
from secrets import token_hex

from src.utils.data_base_util import DataBaseUtil
from src.utils.password_utils import PasswordUtils
from src.backend.exceptions import DuplicationError

# Configure logging
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class User:
    def __init__(self, user_id: str, username: str, password: str, first_name: str, last_name: str,
                bio: str = None, remember_me: bool = False):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.bio = bio or None
        self.remember_me = remember_me

    @classmethod
    def authenticate(cls, username: str, password: str) -> Optional["User"]:
        """
        Authenticate a user by username and password.

        Args:
            username (str): The user's username.
            password (str): The user's password.

        Returns:
            User: The authenticated user object, or None if authentication fails.
        """
        user_data = cls._find_user_by_username(username)
        if user_data is None:
            logger.warning(f"Authentication failed: User '{username}' not found.")
            return None

        user = cls(*user_data)
        if not PasswordUtils.verify_password(password, user.password):
            logger.warning(f"Authentication failed: Incorrect password for user '{username}'.")
            return None

        logger.info(f"User '{username}' authenticated successfully.")
        return user

    @classmethod
    def register_new_user(cls, username: str, password: str, first_name: str, last_name: str,
                          remember_me: bool = False) -> "User":
        """
        Register a new user.

        Args:
            username (str): The username of the new user.
            password (str): The plaintext password for the new user.
            first_name (str): The user's first name.
            last_name (str): The user's last name.
            remember_me (bool): The user's remember me option.

        Returns:
            User: The newly registered user object.

        Raises:
            DuplicationError: If a user with the given username already exists.
        """
        if cls._find_user_by_username(username) is not None:
            raise DuplicationError(f"Registration failed: User '{username}' already exists.")

        hashed_password = PasswordUtils.hash_password(password)
        user_id = cls._generate_unique_user_id()

        cls._save_user(user_id, username, hashed_password, first_name, last_name, remember_me)
        logger.info(f"User '{username}' registered successfully.")
        return cls(user_id, username, hashed_password, first_name, last_name, remember_me=remember_me)

    @classmethod
    def get_user_by_id(cls, user_id: str) -> Optional["User"]:
        """
        Retrieve a user by their ID.

        Args:
            user_id (str): The user's ID.

        Returns:
            User: The user object, or None if no matching user is found.
        """
        user_data = cls._find_user_by_id(user_id)
        if user_data is None:
            logger.warning(f"No user found with ID '{user_id}'.")
            return None

        user_data = {
            "user_id": user_data[0],
            "username": user_data[1],
            "password": user_data[2],
            "first_name": user_data[3],
            "last_name": user_data[4],
            "bio": user_data[5],
            "remember_me": user_data[6]
        }
        user_data.update(cls._extend_fields_by_user_id(user_id))

        return cls(**user_data)

    @classmethod
    def search_saved_users(cls, username_substr: str) -> List["User"]:
        """
        Searches for users whose usernames contain the given substring and have 'remember_me' enabled.

        Args:
            username_substr (str): Substring to search for in usernames.

        Returns:
            List[User]: List of matching user objects.
        """
        users = [cls(*user) for user in cls._get_users_with_remember_me()]
        matching_users = [user for user in users if username_substr.lower() in user.username.lower()]
        return matching_users

    def toggle_remember_me(self) -> None:
        """
        Toggle the 'remember_me' status for the current user.
        """
        self.remember_me = not self.remember_me
        self.update_user_values(self.user_id, {"remember_me": self.remember_me})
        logger.info(f"User '{self.username}' updated 'remember_me' to {self.remember_me}.")

    @staticmethod
    def update_user_values(user_id: str, updates: Dict[str, Any]) -> None:
        """
        Updates fields for a user in the database.

        Args:
            user_id (str): The ID of the user to update.
            updates (Dict[str, Any]): Dictionary of fields and values to update.
        """
        db = DataBaseUtil()
        db.update_one("users", "user_ID", user_id, updates)
        logger.info(f"Updated user data: {updates}")
        db.__del__()

    @staticmethod
    def _find_user_by_username(username: str) -> Optional[List]:
        db = DataBaseUtil()
        try:
            data = db.load_data("users", "username", username)
        except Exception as e:
            data = None
        finally:
            db.__del__()
        return data

    @staticmethod
    def _find_user_by_id(user_id: str) -> Optional[List]:
        db = DataBaseUtil()
        try:
            data = db.load_data("users", "user_ID", user_id)
        except Exception as e:
            data = None
        finally:
            db.__del__()
        return data

    @staticmethod
    def _save_user(user_id: str, username: str, password: str, first_name: str, last_name: str,
                   remember_me: bool = False) -> None:
        user_data = {
            "user_ID": user_id,
            "username": username,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "remember_me": remember_me
        }
        db = DataBaseUtil()
        db.insert_one("users", user_data, "user_ID")
        db.__del__()

    @staticmethod
    def _get_users_with_remember_me() -> List[Dict]:
        db = DataBaseUtil()
        data = db.load_many("users", "remember_me", [True])
        db.__del__()
        return data

    @classmethod
    def _generate_unique_user_id(cls) -> str:
        existing_ids = cls._get_ids()
        while True:
            user_id = token_hex(8)
            if user_id not in existing_ids:
                return user_id

    @classmethod
    def _get_ids(cls) -> set:
        db = DataBaseUtil()
        data = {user[0] for user in db.load_many("users")}
        db.__del__()
        return data

    @staticmethod
    def _extend_fields_by_user_id(user_id: str) -> Dict:
        """
        Placeholder for extending user fields.
        """
        return {}
