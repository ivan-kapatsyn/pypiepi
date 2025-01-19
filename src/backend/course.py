from typing import Optional, List

from src.backend.qualification import Qualification
from src.backend.room import Room
from src.backend.announcement import Announcement
from src.utils.data_base_util import DataBaseUtil
from src.backend.exceptions import DuplicationError
from secrets import token_hex

# Configure logging
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class Course:
    def __init__(self, course_id: str, user_id: str, name: str, qualification: Qualification,
                 room: Room, schedule: str, max_participants: int, description: Optional[str] = None,
                 announcements: Optional[List[Announcement]] = None):
        self.course_id = course_id
        self.user_id = user_id
        self.name = name
        self.qualification = qualification
        self.room = room
        self.schedule = schedule
        self.max_participants = max_participants
        self.description = description or None
        self.announcements = announcements or []

    @classmethod
    def add_new_course(cls, name: str, user_id: str, qualification: Qualification, room_id: str,
                       schedule: str, max_participants: int) -> str:
        """
        Adds a new course to the system.

        Args:
            name (str): Name of the course.
            user_id (str): ID of the tutor creating the course.
            qualification (Qualification): Qualification associated with the course.
            room_id (str): ID of the room where the course will be held.
            schedule (str): Schedule of the course.
            max_participants (int): Maximum number of participants allowed in the course.

        Returns:
            str: The unique ID of the newly created course.

        Raises:
            Exception: If the specified room does not exist.
            DuplicationError: If a course with the same room and schedule already exists.
        """
        if Room.get_room_by_id(room_id) is None:
            raise Exception(f"Room {room_id} does not exist.")

        # TODO change schedule logic
        if cls._is_duplicate(room_id, schedule):
            raise DuplicationError(f"A course in room '{room_id}' at schedule '{schedule}' already exists.")

        course_id = cls._generate_unique_course_id()
        cls._save_course(course_id, user_id, name, qualification, room_id, schedule, max_participants)

        logger.info(f"Course '{name}' added successfully with ID: {course_id}.")
        return course_id

    @classmethod
    def get_course_by_id(cls, course_id: str) -> Optional["Course"]:
        """
        Retrieves a course by its unique ID.

        Args:
            course_id (str): The unique ID of the course to retrieve.

        Returns:
            Optional[Course]: The Course instance if found, otherwise None.
        """
        course_data = cls._find_course_by_id(course_id)
        if course_data is None:
            logger.warning(f"No course found with ID '{course_id}'.")
            return None

        course_data = {
            "course_id": course_id,
            "user_id": course_data[1],
            "name": course_data[2],
            "qualification": Qualification(course_data[3]),
            "room": Room.get_room_by_id(course_data[4]),
            "schedule": course_data[5],
            "max_participants": course_data[6],
            "description": course_data[7],
            "announcements": Announcement.get_announcements_by_course_id(course_id)
        }

        return cls(**course_data)

    @classmethod
    def get_course_by_user_id(cls, user_id: str) -> List["Course"]:
        """
        Retrieves all courses associated with a given user ID.

        Args:
            user_id (str): The unique identifier of the user whose courses are being retrieved.

        Returns:
            List[Course]: A list of `Course` objects corresponding to the courses the user is associated with.
                          If no courses are found, an empty list is returned.
        """
        db = DataBaseUtil()
        try:
            course_data = db.load_many("course")
            courses = []
            for course in course_data:
                if user_id == course[1]:
                    course_data = {
                        "course_id": course[0],
                        "user_id": course[1],
                        "name": course[2],
                        "qualification": Qualification(course[3]),
                        "room": Room.get_room_by_id(course[4]),
                        "schedule": course[5],
                        "max_participants": course[6],
                        "description": course[7],
                        "announcements": Announcement.get_announcements_by_course_id(course[0])
                    }

                    courses.append(cls(**course_data))

            return courses

        except Exception as e:
            logger.error(f"Error retrieving courses for user ID '{user_id}': {e}")
            return []

    def delete_course(self):
        """
        Deletes the course from the system.
        """
        db = DataBaseUtil()
        db.delete_one("course", "course_id", self.course_id)
        logger.info(f"Course with ID '{self.course_id}' deleted successfully.")

    @staticmethod
    def _is_duplicate(room_id: str, schedule: str) -> bool:
        db = DataBaseUtil()
        courses = db.load_many("course")
        for course in courses:
            if course[4] == room_id and schedule == course[5]:
                return True
        return False

    @staticmethod
    def _find_course_by_id(course_id: str) -> Optional[List]:
        db = DataBaseUtil()
        try:
            data = db.load_one("course", "course_ID", course_id)
        except Exception as e:
            data = None
        return data

    @staticmethod
    def _save_course(course_id, user_id, name, qualification, room_id, schedule, max_participants):
        course_data = {
                "course_ID": course_id,
                "user_ID": user_id,
                "name": name,
                "qualifications": qualification.name,
                "room_ID": room_id,
                "schedule": schedule,
                "max_participants": max_participants
        }
        db = DataBaseUtil()
        db.insert_one("course", course_data, "course_ID")

    @staticmethod
    def _generate_unique_course_id() -> str:
        db = DataBaseUtil()
        existing_ids = {course[0] for course in db.load_many("course")}
        while True:
            course_id = token_hex(8)
            if course_id not in existing_ids:
                return course_id
