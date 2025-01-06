import unittest
from unittest.mock import patch
from src.backend.user import Tutor, Qualification, DuplicationError, WrongTokenError


class TestRegisterNewTutor(unittest.TestCase):

    @patch('src.backend.user.register_token_exists')
    @patch('src.backend.user.remove_register_token')
    @patch('src.backend.user.save_user')
    @patch('src.backend.user.save_tutor')
    def test_register_new_tutor_success(self, mock_save_tutor, mock_save_user,
                                        mock_remove_register_token, mock_register_token_exists):
        username = "new_tutor"
        first_name = "John"
        last_name = "Doe"
        password = "password123"
        token = 123
        qualifications = [Qualification("Math")]

        user_id = Tutor.register_new_tutor(username, first_name, last_name, password,
                                           token, qualifications)

        self.assertTrue(user_id)
        self.assertIsInstance(user_id, str)
        mock_register_token_exists.assert_called_once_with(token)
        mock_remove_register_token.assert_called_once_with(token)
        mock_save_user.assert_called_once()
        mock_save_tutor.assert_called_once()

    def test_register_new_tutor_duplicate_username(self):
        username = "user1"
        first_name = "John"
        last_name = "Doe"
        password = "password123"
        tutor_register_number = 123
        qualifications = [Qualification("Math")]

        with self.assertRaises(DuplicationError):
            Tutor.register_new_tutor(username, first_name, last_name, password, tutor_register_number, qualifications)

    def test_register_new_tutor_invalid_token(self):
        username = "new_tutor"
        first_name = "John"
        last_name = "Doe"
        password = "password123"
        tutor_register_number = 99999
        qualifications = [Qualification("Math")]

        with self.assertRaises(WrongTokenError):
            Tutor.register_new_tutor(username, first_name, last_name, password, tutor_register_number, qualifications)

if __name__ == "__main__":
    unittest.main()