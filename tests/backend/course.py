import unittest
from src.backend.qualification import Qualification
from src.backend.course import Course
from src.backend.exceptions import DuplicationError


class TestCourse(unittest.TestCase):

    def test_add_new_course_success(self):
        course_id = Course.add_new_course(
            name="Advanced Programming",
            user_id="430112d4d154a44f",
            qualification=Qualification("Math"),
            room_id="1e06e1ddca76f5d4",
            schedule="sample1",
            max_participants=25
        )

        course = Course.get_course_by_id(course_id)
        self.assertIsNotNone(course)
        self.assertEqual(course.name, "Advanced Programming")
        self.assertEqual(course.room.room_id, "1e06e1ddca76f5d4")
        self.assertEqual(course.schedule, "sample1")
        self.assertEqual(course.max_participants, 25)

    def test_add_new_course_room_not_found(self):
        with self.assertRaises(Exception):
            Course.add_new_course(
                name="Advanced Programming",
                user_id="430112d4d154a44f",
                qualification=Qualification("Math"),
                room_id="nonexistent_room_id",
                schedule="sample2",
                max_participants=25
            )

    def test_add_new_course_duplication_error(self):
        Course.add_new_course(
            name="Advanced Programming",
            user_id="430112d4d154a44f",
            qualification=Qualification("Math"),
            room_id="0fc47a8b9acc2ab3",
            schedule="sample3",
            max_participants=25
        )

        with self.assertRaises(DuplicationError):
            Course.add_new_course(
                name="Data Structures",
                user_id="user2",
                qualification=Qualification("Math"),
                room_id="0fc47a8b9acc2ab3",
                schedule="sample3",
                max_participants=25
            )

    def test_get_course_by_id(self):
        course_id = Course.add_new_course(
            name="Advanced Programming",
            user_id="430112d4d154a44f",
            qualification=Qualification("Math"),
            room_id="0fc47a8b9acc2ab3",
            schedule="sample4",
            max_participants=25
        )

        course = Course.get_course_by_id(course_id)

        self.assertIsNotNone(course)
        self.assertEqual(course.course_id, course_id)
        self.assertEqual(course.name, "Advanced Programming")
        self.assertEqual(course.schedule, "sample4")
        self.assertEqual(course.max_participants, 25)

    def test_delete_course(self):
        course_id = Course.add_new_course(
            name="Advanced Programming",
            user_id="430112d4d154a44f",
            qualification=Qualification("Math"),
            room_id="0fc47a8b9acc2ab3",
            schedule="sample5",
            max_participants=25
        )

        course = Course.get_course_by_id(course_id)
        course.delete_course()

        course = Course.get_course_by_id(course_id)
        self.assertIsNone(course)

    def test_get_courses_by_user_id_success(self):
        user_id = "b365cd8f07cd0520"

        course_id_1 = Course.add_new_course(
            name="Advanced Programming",
            user_id=user_id,
            qualification=Qualification("Math"),
            room_id="0fc47a8b9acc2ab3",
            schedule="sample6",
            max_participants=25
        )

        course_id_2 = Course.add_new_course(
            name="Data Structures",
            user_id=user_id,
            qualification=Qualification("Math"),
            room_id="0fc47a8b9acc2ab3",
            schedule="sample7",
            max_participants=30
        )

        courses = Course.get_courses_by_user_id(user_id)

        self.assertEqual(len(courses), 2)
        self.assertEqual(courses[0].user_id, user_id)
        self.assertEqual(courses[1].user_id, user_id)

    def test_get_courses_by_user_id_no_courses(self):
        courses = Course.get_courses_by_user_id("non_existent_user")
        self.assertEqual(len(courses), 0)



if __name__ == "__main__":
    unittest.main()