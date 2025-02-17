import unittest
from secrets import token_hex
from src.backend.exceptions import DuplicationError
from src.backend.user import User

class TestUser(unittest.TestCase):

    def test_authenticate_success(self):
        user = User.authenticate("john.doe", "newpassword")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "john.doe")

    def test_authenticate_incorrect_password(self):
        user = User.authenticate("john.doe", "wrongpassword")
        self.assertIsNone(user)

    def test_authenticate_user_not_found(self):
        user = User.authenticate("nonexistent", "password123")
        self.assertIsNone(user)

    def test_register_new_user_success(self):
        test_username = token_hex(8)
        user = User.register_new_user(test_username, "newpassword", "Test", "User", remember_me=True)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, test_username)

        saved_user = User.authenticate(test_username, "newpassword")
        self.assertIsNotNone(saved_user)
        self.assertEqual(saved_user.username, test_username)

    def test_register_new_user_duplicate(self):
        with self.assertRaises(DuplicationError):
            User.register_new_user("john.doe", "newpassword", "John", "Doe")

    def test_get_user_by_id_success(self):
        user = User.get_user_by_id("f67d38dee48d641f")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "john.doe")

    def test_get_user_by_id_not_found(self):
        user = User.get_user_by_id("nonexistent_id")
        self.assertIsNone(user)

    def test_search_saved_users(self):
        users = User.search_saved_users("john")
        self.assertEqual(len(users), 1)
        self.assertTrue(all("john" in user.username for user in users))

    def test_toggle_remember_me(self):
        user = User.get_user_by_id("0fd78ece486e8df4")
        initial_status = user.remember_me
        user.toggle_remember_me()
        updated_user = User.get_user_by_id("0fd78ece486e8df4")
        self.assertNotEqual(initial_status, updated_user.remember_me)

    def test_update_user_values_success(self):
        user = User.get_user_by_id("4cb33c4df7a6ad3d")
        updates = {"first_name": "test", "last_name": "name", "bio": "Test bio.", "remember_me": False}

        user.update_user_values(updates)
        updated_user = User.get_user_by_id("4cb33c4df7a6ad3d")

        self.assertEqual(updated_user.first_name, updates["first_name"])
        self.assertEqual(updated_user.last_name, updates["last_name"])
        self.assertEqual(updated_user.bio, updates["bio"])
        self.assertEqual(updated_user.remember_me, updates["remember_me"])

    def test_update_user_values_invalid_field(self):
        user = User.get_user_by_id("4cb33c4df7a6ad3d")
        updates = {"invalid_field": "value"}

        user.update_user_values(updates)
        updated_user = User.get_user_by_id("4cb33c4df7a6ad3d")

        self.assertEqual(user.__dict__, updated_user.__dict__)


if __name__ == "__main__":
    unittest.main()