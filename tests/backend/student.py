import unittest
from secrets import token_hex
from src.backend.student import Student
from src.backend.course import Course
from src.backend.qualification import Qualification
from src.utils.data_base_util import DataBaseUtil
from src.backend.exceptions import DuplicationError


class TestStudentDatabase(unittest.TestCase):

    def test_register_new_student_success(self):
        test_username = token_hex(8)
        user_id = Student.register_new_user(
            username=test_username,
            password="securepassword",
            first_name="Test",
            last_name="Student",
            study_program="Computer Science",
            register_number=111
        )
        self.assertIsNotNone(user_id)

        student = Student.get_user_by_id(user_id)
        self.assertIsNotNone(student)
        self.assertEqual(student.username, test_username)
        self.assertEqual(student.study_program, "Computer Science")
        self.assertEqual(student.register_number, 111)
        self.assertFalse(student.active_courses)

    def test_register_new_student_duplicate_username(self):
        with self.assertRaises(DuplicationError):
            Student.register_new_user(
                username="mary.stuart",
                password="newpassword",
                first_name="Mary",
                last_name="Stuart",
                study_program="Math",
                register_number=123
            )

    def test_get_user_by_id_success(self):
        student = Student.get_user_by_id("968c68d2315a8b10")

        self.assertIsNotNone(student)
        self.assertEqual(student.username, "tony.stark")
        self.assertEqual(student.study_program, "physics")
        self.assertEqual(student.register_number, 72379707)

    def test_find_student_by_user_id_success(self):
        student_id = "f63b0b2f7c48c85f"
        student_data = Student._find_student_by_user_id(student_id)
        self.assertIsNotNone(student_data)
        self.assertEqual(student_data[0], student_id)

    def test_find_student_by_user_id_not_found(self):
        tutor_data = Student._find_student_by_user_id("nonexistent_id")
        self.assertIsNone(tutor_data)

    def test_update_student_values_success(self):
        student = Student.get_user_by_id("f67d38dee48d641f")
        updates = {"study_program": "Philosophy"}

        student.update_user_values(updates)
        updated_student = Student.get_user_by_id("f67d38dee48d641f")

        self.assertEqual(updated_student.study_program, updates["study_program"])
        self.assertEqual(updated_student.first_name, student.first_name)

    def test_update_user_and_student_fields(self):
        student = Student.get_user_by_id("f67d38dee48d641f")
        updates = {"first_name": "Test", "last_name": "Name", "study_program": "Maths"}

        student.update_user_values(updates)
        updated_student = Student.get_user_by_id("f67d38dee48d641f")

        self.assertEqual(updated_student.first_name, updates["first_name"])
        self.assertEqual(updated_student.last_name, updates["last_name"])
        self.assertEqual(updated_student.study_program, updates["study_program"])

    def test_register_for_a_course_success(self):
        student = Student.get_user_by_id("f63b0b2f7c48c85f")
        test_course_id = "74527542b2660b56"

        student.register_for_a_course(test_course_id)

        active_course_ids = {course.course_id for course in student.active_courses}
        self.assertIn(test_course_id, active_course_ids)

    def test_course_capacity_check(self):
        course_id = Course.add_new_course("Test", "b365cd8f07cd0520", Qualification("Test"), "a3cfc82a59a8ea4b", "Mon 10-11", 1)
        student = Student.get_user_by_id("f63b0b2f7c48c85f")
        student.register_for_a_course(course_id)
        student = Student.get_user_by_id("0fd78ece486e8df4")
        student.register_for_a_course(course_id)
        self.assertNotIn(course_id, {course.course_id for course in student.active_courses})
        Course.get_course_by_id(course_id).delete_course()

    def test_unregister_for_a_course_success(self):
        student = Student.get_user_by_id("f63b0b2f7c48c85f")
        test_course_id = "74527542b2660b56"

        student.register_for_a_course(test_course_id)
        student.unregister_for_a_course(test_course_id)

        active_course_ids = {course.course_id for course in student.active_courses}
        self.assertNotIn(test_course_id, active_course_ids)

        course = Course.get_course_by_id(test_course_id)
        self.assertNotIn("f63b0b2f7c48c85f", course.student_ids)

    def test_unregister_for_a_course_not_registered(self):
        student = Student.get_user_by_id("f63b0b2f7c48c85f")
        test_course_id = "nonexistent_course"

        student.unregister_for_a_course(test_course_id)

        self.assertNotIn(test_course_id, {course.course_id for course in student.active_courses})

    def test_leave_feedback_success(self):
        student = Student.get_user_by_id("f63b0b2f7c48c85f")
        course_id = "74527542b2660b56"
        feedback = "This course was great!"
        grade = 9.5

        student.register_for_a_course(course_id)
        student.leave_feedback(course_id, feedback, grade)

        db = DataBaseUtil()
        evaluations = db.load_many("evaluation", "course_id = %s", [course_id])
        latest_feedback = next((record for record in evaluations if record[2] == student.user_id), None)

        self.assertIsNotNone(latest_feedback)
        self.assertEqual(latest_feedback[4], feedback)
        self.assertEqual(latest_feedback[5], grade)

    def test_leave_feedback_grade_boundary(self):
        student = Student.get_user_by_id("f63b0b2f7c48c85f")
        course_id = "74527542b2660b56"
        student.register_for_a_course(course_id)
        with self.assertRaises(ValueError):
            student.leave_feedback(course_id, "Great course", -1)
        with self.assertRaises(ValueError):
            student.leave_feedback(course_id, "Awesome", 11)

    def test_search_from_active_courses_success(self):
        student = Student.get_user_by_id("f63b0b2f7c48c85f")

        test_course_1 = Course.add_new_course("Math 101", "b365cd8f07cd0520", Qualification("Math"), "50ce7062018a8c65",
                                              "Mon 9-11", 25)
        test_course_2 = Course.add_new_course("Physics 101", "b365cd8f07cd0520", Qualification("Physics"), "50ce7062018a8c65",
                                              "Tue 10-12", 25)

        student.register_for_a_course(test_course_1)
        student.register_for_a_course(test_course_2)

        filters = [{"name": ["Math 101"]}]
        courses = student.search_from_active_courses(filters)

        self.assertEqual(len(courses), 1)
        self.assertEqual(courses[0].name, "Math 101")

        Course.get_course_by_id(test_course_1).delete_course()
        Course.get_course_by_id(test_course_2).delete_course()

    def test_search_from_new_courses_success(self):
        student = Student.get_user_by_id("f63b0b2f7c48c85f")

        new_course_1 = Course.add_new_course("Chemistry 101", "b365cd8f07cd0520", Qualification("Chemistry"), "50ce7062018a8c65",
                                             "Wed 13-15", 30)
        new_course_2 = Course.add_new_course("Biology 101", "b365cd8f07cd0520", Qualification("Biology"), "50ce7062018a8c65",
                                             "Thu 14-16", 30)

        filters = [{"name": ["Chemistry 101", "Biology 101"]}]
        courses = student.search_from_new_courses(filters)

        course_names = {course.name for course in courses}
        self.assertIn("Chemistry 101", course_names)
        self.assertIn("Biology 101", course_names)

        Course.get_course_by_id(new_course_1).delete_course()
        Course.get_course_by_id(new_course_2).delete_course()

    def test_search_from_active_courses_no_match(self):
        student = Student.get_user_by_id("f63b0b2f7c48c85f")
        filters = [{"name": ["Nonexistent Course"]}]
        courses = student.search_from_active_courses(filters)
        self.assertEqual(len(courses), 0)

    def test_search_from_new_courses_no_match(self):
        student = Student.get_user_by_id("f63b0b2f7c48c85f")
        filters = [{"name": ["Nonexistent Course"]}]
        courses = student.search_from_new_courses(filters)
        self.assertEqual(len(courses), 0)

if __name__ == "__main__":
    unittest.main()