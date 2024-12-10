# TODO data_base_util Dummy
from src.backend.data_base_util import find_user_by_username, save_user, users_with_remember_me, get_user_ids

from src.utils.password_utils import PasswordUtils
from typing import List
from secrets import token_hex


# TODO put later elsewhere
class DuplicationError(Exception):
    pass

class User:
    def __init__(self, user_id: str, username: str, password: str, remember_me: bool = False):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.remember_me = remember_me

    @classmethod
    def authenticate(cls, username: str, password: str):
        """
        Returns a user instance if authentication is successful, None otherwise.
        """

        user_data = find_user_by_username(username)
        if not user_data:
            return None

        if PasswordUtils.verify_password(password, user_data["password"]):
            return cls(user_data["user_id"], user_data["username"], user_data["password"],
                       user_data.get("remember_me", False))
        return None

    @classmethod
    def register_new_user(cls, username: str, password: str, remember_me: bool = False):
            """
            Raises DuplicationError if a user with the same username already exists.

            Returns an instance of the created User.
            """

            if find_user_by_username(username):
                raise DuplicationError(f"User with username '{username}' already exists.")

            hashed_password = PasswordUtils.hash_password(password)

            user_ids = get_user_ids()
            while True:
                new_user_id = cls.generate_user_id()
                if new_user_id not in user_ids:
                    break

            new_user_data = {"user_id": new_user_id, "username": username, "password": hashed_password,
                             "remember_me": remember_me}

            save_user(new_user_data)
            return cls(new_user_id, username, hashed_password, remember_me)

    @classmethod
    def search_for_a_saved_users(cls, username_substr: str) -> List["User"]:
        """
        Returns a list of matching User instances.
        """

        users_data = users_with_remember_me()

        # TODO remake on the data base side
        matching_users = [user for user in users_data if user["username"].startswith(username_substr.lower())]

        return [cls(user["user_id"], user["username"], user["password"], user["remember_me"])
                for user in matching_users]

    @staticmethod
    def generate_user_id() -> str:
        """
        Returns a random 16-character string
        """
        return token_hex(8)
