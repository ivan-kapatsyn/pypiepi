import unittest
from datetime import datetime
from src.backend.announcement import Announcement
from src.backend.course import Course
from src.backend.qualification import Qualification


class TestAnnouncement(unittest.TestCase):

    def test_add_new_announcement_success(self):
        course_id = "f61985b87284171a"
        message = "New course material is available."
        announcement_id = Announcement.add_new_announcement(course_id, message)

        announcement = Announcement.get_announcement_by_id(announcement_id)

        self.assertIsNotNone(announcement)
        self.assertEqual(announcement.course_id, course_id)
        self.assertEqual(announcement.message, message)
        self.assertIsInstance(announcement.date, datetime)

    def test_get_announcement_by_id_not_found(self):
        non_existent_announcement_id = "non_existent_announcement_id"
        announcement = Announcement.get_announcement_by_id(non_existent_announcement_id)

        self.assertIsNone(announcement)

    def test_get_announcements_by_course_id(self):
        course_id = Course.add_new_course("test", "430112d4d154a44f", Qualification("Math"),
                                          "1e06e1ddca76f5d4", "Mon9-12", 25)
        message_1 = "First announcement."
        message_2 = "Second announcement."

        announcement_id_1 = Announcement.add_new_announcement(course_id, message_1)
        announcement_id_2 = Announcement.add_new_announcement(course_id, message_2)

        announcements = Announcement.get_announcements_by_course_id(course_id)

        self.assertEqual(len(announcements), 2)

        self.assertEqual(announcements[0].course_id, course_id)
        self.assertEqual(announcements[0].message, message_1)

        self.assertEqual(announcements[1].course_id, course_id)
        self.assertEqual(announcements[1].message, message_2)

    def test_get_announcements_by_course_id_empty(self):
        course_id = "course_not_found"
        announcements = Announcement.get_announcements_by_course_id(course_id)

        self.assertEqual(announcements, [])


if __name__ == "__main__":
    unittest.main()