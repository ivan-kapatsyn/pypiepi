import unittest
from src.backend.exceptions import DuplicationError
from src.backend.user import User

class TestUserDatabase(unittest.TestCase):

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
        user = User.register_new_user("new.user", "newpassword", "New", "User", remember_me=True)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "new.user")

        saved_user = User.authenticate("new.user", "newpassword")
        self.assertIsNotNone(saved_user)
        self.assertEqual(saved_user.username, "new.user")

    def test_register_new_user_duplicate(self):
        with self.assertRaises(DuplicationError):
            User.register_new_user("john.doe", "newpassword", "John", "Doe")

    def test_get_user_by_id_success(self):
        user = User.get_user_by_id("299edbe2695a53ed")
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
        user = User.get_user_by_id("a70030991cfada5a")
        initial_status = user.remember_me
        user.toggle_remember_me()
        updated_user = User.get_user_by_id("a70030991cfada5a")
        self.assertNotEqual(initial_status, updated_user.remember_me)

if __name__ == "__main__":
    unittest.main()