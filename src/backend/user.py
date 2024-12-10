# TODO data_base_util Dummy
from src.backend.data_base_util import find_user_by_username, save_user, users_with_remember_me

from src.backend.password_utils import verify_password, hash_password
from typing import List


class DuplicationError(Exception):
    pass

class User:
    def __init__(self, username: str, password: str, remember_me: bool = False):
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

        if verify_password(password, user_data["password"]):
            return cls(user_data["username"], user_data["password"], user_data.get("remember_me", False))
        return None

    @classmethod
    def register_new_user(cls, username: str, password: str, remember_me: bool = False):
            """
            Raises DuplicationError if a user with the same username already exists.

            Returns an instance of the created User.
            """

            if find_user_by_username(username):
                raise DuplicationError(f"User with username '{username}' already exists.")

            hashed_password = hash_password(password)
            new_user_data = {"username": username, "password": hashed_password, "remember_me": remember_me}

            save_user(new_user_data)
            return cls(username, hashed_password, remember_me)

    @classmethod
    def search_for_a_saved_users(cls, username_substr: str) -> List["User"]:
        """
        Returns a list of matching User instances.
        """

        users_data = users_with_remember_me()

        matching_users = [user for user in users_data if user["username"].startswith(username_substr.lower())]

        return [cls(user["username"], user["password"], user["remember_me"]) for user in matching_users]
