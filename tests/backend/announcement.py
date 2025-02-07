import unittest
from datetime import datetime
from src.backend.announcement import Announcement


class TestAnnouncement(unittest.TestCase):

    def test_add_new_announcement_success(self):
        course_id = "b365cd8f07cd0520"
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
        course_id = "f61985b87284171a"
        announcements = Announcement.get_announcements_by_course_id(course_id)

        self.assertEqual(len(announcements), 2)

        self.assertEqual(announcements[0].course_id, course_id)
        self.assertIsInstance(announcements[0].date, datetime)
        self.assertEqual(announcements[0].message, "First announcement.")

        self.assertEqual(announcements[1].course_id, course_id)
        self.assertIsInstance(announcements[0].date, datetime)
        self.assertEqual(announcements[1].message, "Second announcement.")

    def test_get_announcements_by_course_id_empty(self):
        course_id = "course_not_found"
        announcements = Announcement.get_announcements_by_course_id(course_id)

        self.assertEqual(announcements, [])


if __name__ == "__main__":
    unittest.main()