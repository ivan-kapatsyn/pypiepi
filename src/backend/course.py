from typing import Optional, List
from datetime import datetime, timedelta

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
    def get_courses_by_user_id(cls, user_id: str) -> List["Course"]:
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
            course_data = db.load_many("course", "user_id = %s", [user_id])

            return [
                cls(
                    course_id=course[0],
                    user_id=course[1],
                    name=course[2],
                    qualification=Qualification(course[3]),
                    room=Room.get_room_by_id(course[4]),
                    schedule=course[5],
                    max_participants=course[6],
                    description=course[7],
                    announcements=Announcement.get_announcements_by_course_id(course[0]),
                )
                for course in course_data
            ]

        except Exception as e:
            logger.warning(f"Error retrieving courses for user_id {user_id}: {e}")
            return []

    @classmethod
    def get_courses_by_schedule(cls, day: str, start_hour: str) -> List["Course"]:
        """
        Retrieves all courses associated with a given schedule.

        Args:
            :param start_hour: A starting hour for the courses.
            :param day: A day code of the schedule (e.g. Mon)

        Returns:
            List[Course]: A list of `Course` objects corresponding to the courses, where the schedule day coincide
            and start hour is inside the time range

        """
        db = DataBaseUtil()
        try:
            course_data = db.load_many("course", "schedule LIKE %s", [f'{day}%'])

            return [
                cls(
                    course_id=course[0],
                    user_id=course[1],
                    name=course[2],
                    qualification=Qualification(course[3]),
                    room=Room.get_room_by_id(course[4]),
                    schedule=course[5],
                    max_participants=course[6],
                    description=course[7],
                    announcements=Announcement.get_announcements_by_course_id(course[0]),
                )
                for course in course_data if cls.__check_if_start_hour_inside_time_range(start_hour, course[5])
            ]

        except Exception as e:
            logger.error(f"Error retrieving courses for schedule {day}, {start_hour}. The reason is {e}")
            return []

    @classmethod
    def get_courses_by_name_start(cls, name_start: str) -> List["Course"]:
        """
        Retrieves all courses associated with a given name.

        Args:
            :param name_start: A starting hour for the courses.

        Returns:
            List[Course]: A list of `Course` objects corresponding to the courses, where the course name starts with given argument

        """
        db = DataBaseUtil()
        try:
            course_data = db.load_many("course", 'LOWER(name) LIKE %s', [f'{name_start.lower()}%'])

            return [
                cls(
                    course_id=course[0],
                    user_id=course[1],
                    name=course[2],
                    qualification=Qualification(course[3]),
                    room=Room.get_room_by_id(course[4]),
                    schedule=course[5],
                    max_participants=course[6],
                    description=course[7],
                    announcements=Announcement.get_announcements_by_course_id(course[0]),
                )
                for course in course_data
            ]

        except Exception as e:
            logger.error(f"Error retrieving courses for the name {name_start}. The reason is {e}")
            return []

    def delete_course(self):
        """
        Deletes the course from the system.
        """
        db = DataBaseUtil()
        db.delete_many("student_in_course", "course_id", [self.course_id])
        db.delete_many("announcement", "course_id", [self.course_id])
        db.delete_many("evaluation", "course_id", [self.course_id])
        db.delete_many("course", "course_id", [self.course_id])
        logger.info(f"Course with ID '{self.course_id}' deleted successfully.")

    @classmethod
    def _is_duplicate(cls, room_id: str, schedule: str) -> bool:
        db = DataBaseUtil()
        courses = db.load_many("course")

        room_schedules = [
            course[5] for course in courses if course[4] == room_id
        ]
        room_schedules.append(schedule)

        if cls.__check_overlaps(room_schedules):
            return True
        return False

    @classmethod
    def __check_overlaps(cls, schedules: list[str]) -> bool:
        parsed_schedules = [cls.__parse_range(s) for s in schedules]
        parsed_schedules.sort(key=lambda x: x[0])

        for i in range(len(parsed_schedules) - 1):
            current_end = parsed_schedules[i][1]
            next_start = parsed_schedules[i + 1][0]
            if current_end > next_start:
                return True
        return False

    @staticmethod
    def __parse_range(schedule: str):
        """
        Expected format: "Mon 9-12".
        """
        try:
            day_map = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
            day, time_range = schedule.split()
            start_time, end_time = time_range.split('-')

            reference_date = datetime(2023, 1, 2)  # Monday, January 2, 2023
            day_offset = timedelta(days=day_map[day])

            if not (0 <= int(start_time) < 24) or not (0 <= int(end_time) < 24):
                raise ValueError(f"Invalid hour in schedule: {schedule}")

            start_datetime = reference_date + day_offset + timedelta(hours=int(start_time))
            end_datetime = reference_date + day_offset + timedelta(hours=int(end_time))

            return start_datetime, end_datetime
        except ValueError as e:
            raise ValueError(f"Invalid schedule format: {schedule}. Error: {e}")

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


    @classmethod
    def __check_if_start_hour_inside_time_range(cls, start_hour, schedule):
        time_range = schedule[4:]
        start, end = time_range.split('-')
        return int(start) <= int(start_hour) < int(end)

    @property
    def student_ids(self):
        db = DataBaseUtil()
        students_in_course = db.load_many('student_in_course', "course_id = %s", [self.course_id])
        student_ids = [student[2] for student in students_in_course]
        return student_ids
