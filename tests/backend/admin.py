import unittest
from secrets import token_hex
from src.backend.admin import Admin
from src.backend.tutor import Tutor
from src.backend.user import User
from src.backend.room import Room
from src.backend.qualification import Qualification
from src.backend.course import Course
from src.utils.data_base_util import DataBaseUtil
from src.backend.exceptions import DuplicationError


class TestAdminDatabase(unittest.TestCase):

    def test_register_new_admin_success(self):
        test_username = token_hex(8)
        user_id = Admin.register_new_user(
            username=test_username,
            password="securepassword",
            first_name="Test",
            last_name="Admin",
            role="superuser"
        )
        self.assertIsNotNone(user_id)

        admin = Admin.get_user_by_id(user_id)
        self.assertIsNotNone(admin)
        self.assertEqual(admin.username, test_username)
        self.assertEqual(admin.role, "superuser")

    def test_register_new_admin_duplicate_username(self):
        with self.assertRaises(DuplicationError):
            Admin.register_new_user(
                username="john.doe",
                password="newpassword",
                first_name="New",
                last_name="Admin",
                role="moderator"
            )

    def test_banish_user_success(self):
        token = 123456789
        Admin.add_token(token)
        test_username = token_hex(8)

        user_id = Tutor.register_new_user(test_username, "newpassword",
                                          "Test", "Tutor", token,
                                          [Qualification("Math"), Qualification("Physics")])
        test_room_id = Room.add_new_room(token_hex(8))
        course_id = Course.add_new_course(
            name="Advanced Programming",
            user_id=user_id,
            qualification=Qualification("Math"),
            room_id=test_room_id,
            schedule="Fri 12-14",
            max_participants=25
        )

        Admin.banish_user(user_id)

        tutor = Tutor.get_user_by_id(user_id)
        course = Course.get_course_by_id(course_id)
        self.assertIsNone(tutor)
        self.assertIsNone(course)

    def test_banish_user_not_found(self):
        user_id = "non_existent_user_id"
        with self.assertRaises(ValueError):
            Admin.banish_user(user_id)

    def test_search_for_user_success(self):
        test_username = token_hex(8)
        User.register_new_user(
            username=test_username,
            password="securepassword",
            first_name="Test",
            last_name="User",
        )
        User.register_new_user(
            username=test_username + "123",
            password="securepassword",
            first_name="Test",
            last_name="User",
        )

        users = Admin.search_for_user(test_username[:3])
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0].username, test_username)

    def test_search_for_user_not_found(self):
        users = Admin.search_for_user("nonexistentusername")
        self.assertEqual(len(users), 0)

    def test_find_courses_at_some_time_success(self):
        course1_id = Course.add_new_course("Intro to Programming", "430112d4d154a44f", Qualification("CS"), "8386436599a51b1b",
                                           "Mon 9-12", 30)
        course2_id = Course.add_new_course("Data Structures", "f63b0b2f7c48c85f", Qualification("CS"), "cb352106bf060d03",
                                           "Mon 10-12", 30)
        course3_id = Course.add_new_course("Algorithms", "b365cd8f07cd0520", Qualification("CS"), "8386436599a51b1b", "Mon 13-15",
                                           30)

        courses = Admin.find_courses_at_some_time("Mon 10")

        self.assertGreaterEqual(len(courses), 2)
        self.assertTrue(any(course.course_id == course2_id for course in courses))
        self.assertTrue(any(course.course_id == course1_id for course in courses))
        Course.get_course_by_id(course1_id).delete_course()
        Course.get_course_by_id(course2_id).delete_course()
        Course.get_course_by_id(course3_id).delete_course()

    def test_find_courses_at_some_time_no_match(self):
        courses = Admin.find_courses_at_some_time("Mon 15")
        self.assertEqual(len(courses), 0)

    def test_add_token_success(self):
        token = 123456
        Admin.add_token(token)

        db = DataBaseUtil()
        tokens = db.load_many("tokens", "token = %s", [token])
        self.assertGreater(len(tokens), 0)

    def test_add_token_duplicate(self):
        token = 123456
        Admin.add_token(token)
        Admin.add_token(token)

        db = DataBaseUtil()
        tokens = db.load_many("tokens", "token = %s", [token])
        self.assertEqual(len(tokens), 1)

if __name__ == "__main__":
    unittest.main()