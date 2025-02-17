import unittest
from secrets import token_hex
from src.backend.tutor import Tutor
from src.backend.admin import Admin
from src.backend.qualification import Qualification
from src.backend.exceptions import DuplicationError, WrongTokenError

class TestTutor(unittest.TestCase):

    def test_register_new_tutor_success(self):
        token = 123456789
        Admin.add_token(token)
        test_username = token_hex(8)

        user_id = Tutor.register_new_user(test_username,"newpassword",
                                           "Test","Tutor", token,
                                           [Qualification("Math"), Qualification("Physics")])
        self.assertIsNotNone(user_id)

        tutor = Tutor.get_user_by_id(user_id)
        self.assertIsNotNone(tutor)
        self.assertEqual(tutor.username, test_username)
        self.assertEqual(tutor.qualifications[0].name, "Math")
        self.assertEqual(tutor.qualifications[1].name, "Physics")

        self.assertNotIn(token, Tutor._get_tokens())

    def test_register_new_tutor_duplicate_username(self):
        with self.assertRaises(DuplicationError):
            Tutor.register_new_user(
                "mary.stuart",
                "newpassword",
                "Mary",
                "Stuart",
                123,
                [Qualification("Math")]
            )

    def test_register_new_tutor_invalid_token(self):
        with self.assertRaises(WrongTokenError):
                Tutor.register_new_user(
                    "invalid.token",
                    "password",
                    "Invalid",
                    "Token",
                    99999,  # Non-existent token
                    [Qualification("Math")]
                )

    def test_register_new_tutor_removes_token(self):
        token = 123456789
        Admin.add_token(token)
        test_username = token_hex(8)

        Tutor.register_new_user(
            test_username,
            "removetoken",
            "Remove",
            "Token",
            token,
            [Qualification("Math")]
        )

        tokens = Tutor._get_tokens()
        self.assertNotIn(token, tokens)

    def test_get_user_by_id_success(self):
        tutor = Tutor.get_user_by_id("b365cd8f07cd0520")

        self.assertIsNotNone(tutor)
        self.assertEqual(tutor.username, "john.marston")
        self.assertEqual(tutor.qualifications[0].name, "computer science")

    def test_find_tutor_by_user_id_success(self):
        tutor_id = "430112d4d154a44f"
        tutor_data = Tutor._find_tutor_by_user_id(tutor_id)
        self.assertIsNotNone(tutor_data)
        self.assertEqual(tutor_data[0], tutor_id)

    def test_find_tutor_by_user_id_not_found(self):
        tutor_data = Tutor._find_tutor_by_user_id("nonexistent_id")
        self.assertIsNone(tutor_data)

    def test_update_tutor_values_success(self):
        tutor = Tutor.get_user_by_id("14d099c161cf3bea")
        updates = {"qualification": [Qualification("Test1"), Qualification("Test2")]}

        tutor.update_user_values(updates)
        updated_tutor = Tutor.get_user_by_id("14d099c161cf3bea")

        self.assertEqual(updated_tutor.qualifications[0].name, updates["qualification"][0].name)
        self.assertEqual(updated_tutor.qualifications[1].name, updates["qualification"][1].name)
        self.assertEqual(updated_tutor.first_name, tutor.first_name)

    def test_update_user_and_tutor_fields(self):
        tutor = Tutor.get_user_by_id("14d099c161cf3bea")
        updates = {"first_name": "Test", "last_name": "Name", "qualification": [Qualification("Test3"), Qualification("Test4")]}

        tutor.update_user_values(updates)
        updated_tutor = Tutor.get_user_by_id("14d099c161cf3bea")

        self.assertEqual(updated_tutor.first_name, updates["first_name"])
        self.assertEqual(updated_tutor.last_name, updates["last_name"])
        self.assertEqual(updated_tutor.qualifications[0].name, updates["qualification"][0].name)
        self.assertEqual(updated_tutor.qualifications[1].name, updates["qualification"][1].name)


if __name__ == "__main__":
    unittest.main()