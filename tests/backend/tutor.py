import unittest
from src.backend.tutor import Tutor
from src.backend.qualification import Qualification
from src.backend.exceptions import DuplicationError, WrongTokenError

class TestTutorDatabase(unittest.TestCase):

    def test_register_new_tutor_success(self):
        token = 111
        user_id = Tutor.register_new_tutor("tutor.new","newpassword",
                                           "New","Tutor", token,
                                           [Qualification("Math")])
        self.assertIsNotNone(user_id)

        tutor = Tutor.get_user_by_id(user_id)
        self.assertIsNotNone(tutor)
        self.assertEqual(tutor.username, "tutor.new")
        self.assertEqual(tutor.qualifications[0].name, "Math")

    def test_register_new_tutor_duplicate_username(self):
        with self.assertRaises(DuplicationError):
            Tutor.register_new_tutor(
                "mary.stuart",
                "newpassword",
                "Mary",
                "Stuart",
                123,
                [Qualification("Math")]
            )

    def test_register_new_tutor_invalid_token(self):
            with self.assertRaises(WrongTokenError):
                Tutor.register_new_tutor(
                    "invalid.token",
                    "password",
                    "Invalid",
                    "Token",
                    99999,  # Non-existent token
                    [Qualification("Math")]
                )

    def test_register_new_tutor_removes_token(self):
        token = 123
        Tutor.register_new_tutor(
            "tutor.removetoken",
            "removetoken",
            "Remove",
            "Token",
            token,
            [Qualification("Math")]
        )

        tokens = Tutor._get_tokens()
        self.assertNotIn(token, tokens)

    def test_find_tutor_by_user_id_success(self):
        tutor_id = "430112d4d154a44f"
        tutor_data = Tutor._find_tutor_by_user_id(tutor_id)
        self.assertIsNotNone(tutor_data)
        self.assertEqual(tutor_data[0], tutor_id)

    def test_find_tutor_by_user_id_not_found(self):
        tutor_data = Tutor._find_tutor_by_user_id("nonexistent_id")
        self.assertIsNone(tutor_data)

if __name__ == "__main__":
    unittest.main()