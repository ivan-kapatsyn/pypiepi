import unittest
from secrets import token_hex
from src.backend.qualification import Qualification
from src.backend.course import Course
from src.backend.room import Room
from src.backend.exceptions import DuplicationError


class TestCourse(unittest.TestCase):

    def test_add_new_course_success(self):
        test_room_id = Room.add_new_room(token_hex(8))

        course_id = Course.add_new_course(
            name="Advanced Programming",
            user_id="430112d4d154a44f",
            qualification=Qualification("Math"),
            room_id=test_room_id,
            schedule="Tue 12-14",
            max_participants=25
        )

        course = Course.get_course_by_id(course_id)
        self.assertIsNotNone(course)
        self.assertEqual(course.name, "Advanced Programming")
        self.assertEqual(course.room.room_id, test_room_id)
        self.assertEqual(course.schedule, "Tue 12-14")
        self.assertEqual(course.max_participants, 25)
        course.delete_course()

    def test_add_new_course_room_not_found(self):
        with self.assertRaises(Exception):
            Course.add_new_course(
                name="Advanced Programming",
                user_id="430112d4d154a44f",
                qualification=Qualification("Math"),
                room_id="nonexistent_room_id",
                schedule="Fri 12-14",
                max_participants=25
            )

    def test_add_new_course_duplication_error(self):
        existing_course = Course.get_course_by_id("f61985b87284171a")
        with self.assertRaises(DuplicationError):
            Course.add_new_course(
                name=existing_course.name,
                user_id=existing_course.user_id,
                qualification=existing_course.qualification,
                room_id=existing_course.room.room_id,
                schedule=existing_course.schedule,
                max_participants=existing_course.max_participants
            )

    def test_add_new_course_schedule_overlapping(self):
        existing_course = Course.get_course_by_id("f61985b87284171a")
        with self.assertRaises(DuplicationError):
            Course.add_new_course(
                name=existing_course.name,
                user_id=existing_course.user_id,
                qualification=existing_course.qualification,
                room_id=existing_course.room.room_id,
                schedule="Mon 8-10",
                max_participants=existing_course.max_participants
            )

        with self.assertRaises(DuplicationError):
            Course.add_new_course(
                name=existing_course.name,
                user_id=existing_course.user_id,
                qualification=existing_course.qualification,
                room_id=existing_course.room.room_id,
                schedule="Mon 10-11",
                max_participants=existing_course.max_participants
            )

        with self.assertRaises(DuplicationError):
            Course.add_new_course(
                name=existing_course.name,
                user_id=existing_course.user_id,
                qualification=existing_course.qualification,
                room_id=existing_course.room.room_id,
                schedule="Mon 7-14",
                max_participants=existing_course.max_participants
            )

    def test_get_course_by_id(self):
        course = Course.get_course_by_id("f61985b87284171a")

        self.assertIsNotNone(course)
        self.assertEqual(course.course_id, "f61985b87284171a")
        self.assertEqual(course.name, "Math couse for begginers")
        self.assertEqual(course.schedule, "Mon 9-12")
        self.assertEqual(course.max_participants, 25)

    def test_delete_course(self):
        course_id = Course.add_new_course(
            name="Advanced Programming",
            user_id="14d099c161cf3bea",
            qualification=Qualification("Math"),
            room_id="0fc47a8b9acc2ab3",
            schedule="Thu 12-14",
            max_participants=25
        )

        course = Course.get_course_by_id(course_id)
        course.delete_course()

        course = Course.get_course_by_id(course_id)
        self.assertIsNone(course)

    def test_get_courses_by_user_id_success(self):
        user_id = "b365cd8f07cd0520"
        courses = Course.get_courses_by_user_id(user_id)

        self.assertEqual(len(courses), 3)
        self.assertEqual(courses[0].user_id, user_id)
        self.assertEqual(courses[1].user_id, user_id)

    def test_get_courses_by_user_id_no_courses(self):
        courses = Course.get_courses_by_user_id("non_existent_user")
        self.assertEqual(len(courses), 0)


    def test_get_courses_by_schedule(self):
        course_list = Course.get_courses_by_schedule('Mon', '10')
        self.assertIsNotNone(course_list)
        self.assertGreater(len(course_list), 0)
        

    def test_student_ids(self):
        course_id = "f61985b87284171a"
        course = Course.get_course_by_id(course_id)

        self.assertGreater(len(course.student_ids), 10)



if __name__ == "__main__":
    unittest.main()