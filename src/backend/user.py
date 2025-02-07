from typing import List, Optional, Dict, Any, Tuple
from secrets import token_hex
from json import dumps
from datetime import datetime, date

from src.utils.data_base_util import DataBaseUtil
from src.utils.password_utils import PasswordUtils
from src.backend.exceptions import DuplicationError

# Configure logging
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class User:
    changeable_user_fields = {"password", "first_name", "last_name", "bio", "remember_me"}
    changeable_type_fields = {}

    def __init__(self, user_id: str, username: str, password: str, first_name: str, last_name: str, registered_at: date,
                bio: str = None, remember_me: bool = False, user_type: str = None):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.registered_at = registered_at
        self.bio = bio or None
        self.remember_me = remember_me
        self.user_type = user_type or None

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

        user = cls.get_user_by_id(user_data[0])
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
        registered_at = datetime.now().date()

        cls._save_user(user_id, username, password, first_name, last_name, registered_at, remember_me)
        logger.info(f"User '{username}' registered successfully.")
        return cls(user_id, username, hashed_password, first_name, last_name, registered_at, remember_me=remember_me)

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
            "remember_me": user_data[6],
            "user_type": user_data[7],
            "registered_at": user_data[8]
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
        self.update_user_values({"remember_me": self.remember_me})
        logger.info(f"User '{self.username}' updated 'remember_me' to {self.remember_me}.")

    def update_user_values(self, updates: Dict[str, Any]) -> None:
        """
        Updates fields for a user in the database.

        Args:
            updates (Dict[str, Any]): Dictionary of fields and values to update.
        """
        updates = self.__validate_updates(updates)

        user_field_updates, type_specific_updates = self.__split_updates(updates)
        type_specific_updates = self._prepare_for_jsonb(type_specific_updates)

        db = DataBaseUtil()

        if user_field_updates:
            db.update_one("users", "user_ID", self.user_id, user_field_updates)

        if type_specific_updates:
            db.update_one(self.user_type, "user_ID", self.user_id, type_specific_updates)

        logger.info(f"Updated user data: {updates}")

    def __validate_updates(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        allowed_fields = self.changeable_user_fields.union(self.changeable_type_fields)

        validated_updates = {k: v for k, v in updates.items() if k in allowed_fields}

        invalid_fields = set(updates) - set(validated_updates)
        if invalid_fields:
            logger.warning(f"Ignored invalid fields: {invalid_fields}.")

        return validated_updates

    def __split_updates(self, updates: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        type_fields = updates.keys() - self.changeable_user_fields

        user_fields_updates = {k: updates[k] for k in self.changeable_user_fields if k in updates}
        type_specific_updates = {k: updates[k] for k in type_fields}

        return user_fields_updates, type_specific_updates

    @staticmethod
    def _prepare_for_jsonb(fields: dict) -> dict:
        if "qualification" in fields:
            fields["qualification"] = dumps(fields["qualification"])
        return fields

    @staticmethod
    def _find_user_by_username(username: str) -> Optional[List]:
        db = DataBaseUtil()
        try:
            data = db.load_one("users", "username", username)
        except Exception as e:
            data = None
        return data

    @staticmethod
    def _find_user_by_id(user_id: str) -> Optional[List]:
        db = DataBaseUtil()
        try:
            data = db.load_one("users", "user_ID", user_id)
        except Exception as e:
            data = None
        return data

    @staticmethod
    def _save_user(user_id: str, username: str, password: str, first_name: str, last_name: str, registered_at: date,
                   remember_me: bool = False, user_type: str = None) -> None:
        user_data = {
            "user_ID": user_id,
            "username": username,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "remember_me": remember_me,
            "user_type": user_type,
            "registered_at": registered_at
        }
        db = DataBaseUtil()
        db.insert_one("users", user_data, "user_ID")

    @staticmethod
    def _get_users_with_remember_me() -> List[Dict]:
        db = DataBaseUtil()
        data = db.load_many("users", "remember_me", [True])
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
        return data

    @staticmethod
    def _extend_fields_by_user_id(user_id: str) -> Dict:
        """
        Placeholder for extending user fields.
        """
        return {}
