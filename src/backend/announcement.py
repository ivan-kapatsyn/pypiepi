from typing import Optional, List
from secrets import token_hex
from datetime import datetime
from src.utils.data_base_util import DataBaseUtil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Announcement:
    def __init__(self, announcement_id: str, course_id, date: datetime, message: str):
        self.announcement_id = announcement_id
        self.course_id = course_id
        self.date = date
        self.message = message

    @staticmethod
    def add_new_announcement(course_id: str, message: str) -> str:
        """
        Adds a new announcement to the database.

        Args:
            course_id (str): The unique identifier of the associated course.
            message (str): The content of the announcement.

        Returns:
            str: The unique ID of the newly created announcement.
        """
        announcement_id = Announcement._generate_unique_announcement_id()
        date = datetime.now()

        db = DataBaseUtil()
        db.insert_one("announcement", {
            "announcement_ID": announcement_id,
            "course_id": course_id,
            "date": date.isoformat(),
            "message": message
        }, "announcement_ID")
        logger.info(f"Announcement added successfully with ID '{announcement_id}'.")

        return announcement_id

    @classmethod
    def get_announcement_by_id(cls, announcement_id: str) -> Optional["Announcement"]:
        """
        Retrieves an announcement by its unique ID.

        Args:
            announcement_id (str): The unique ID of the announcement to retrieve.

        Returns:
            Optional[Announcement]: The Announcement instance if found, otherwise None.
        """
        announcement_data = cls._find_announcement_by_id(announcement_id)
        if announcement_data is None:
            logger.warning(f"No announcement found with ID '{announcement_id}'.")
            return None

        announcement_date = datetime.fromisoformat(announcement_data[2])
        return cls(announcement_id=announcement_data[0], course_id=announcement_data[1], date=announcement_date,
                   message=announcement_data[3])

    @staticmethod
    def get_announcements_by_course_id(course_id: str) -> List["Announcement"]:
        """
        Retrieves all announcements associated with a specific course.

        Args:
            course_id (str): The unique ID of the course.

        Returns:
            List[Announcement]: A list of Announcement instances associated with the course.
        """
        db = DataBaseUtil()
        try:
            announcements_data = db.load_many("announcement", "course_id = %s", [course_id])

            return [
                Announcement(
                    announcement_id=data[0],
                    course_id=data[1],
                    date=datetime.fromisoformat(data[2]),
                    message=data[3]
                )
                for data in announcements_data
            ]

        except Exception as e:
            logger.error(f"Error retrieving announcements for course ID '{course_id}': {e}")
            return []

    @staticmethod
    def _find_announcement_by_id(announcement_id: str) -> Optional[List]:
        db = DataBaseUtil()
        try:
            data = db.load_one("announcement", "announcement_ID", announcement_id)
        except Exception as e:
            logger.error(f"Error retrieving announcement with ID '{announcement_id}': {e}")
            data = None
        return data

    @staticmethod
    def _generate_unique_announcement_id() -> str:
        db = DataBaseUtil()
        existing_ids = {announcement[0] for announcement in db.load_many("announcement")}
        while True:
            announcement_id = token_hex(8)
            if announcement_id not in existing_ids:
                return announcement_id