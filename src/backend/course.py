# TODO data_base_util Dummy
from src.backend.data_base_util import add_student_to_course

from src.backend.qualification import Qualification
from src.backend.time_window import TimeWindow
from src.backend.room import Room
from src.backend.evaluation import Evaluation
from src.backend.user import Tutor, Student

from typing import Optional, List, Union
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Course:
    def __init__(self, name: str, qualification: "Qualification", max_participants: int, tutor: Tutor,
                 students: Optional[List["Student"]] = None,
                 schedule: Optional[List["TimeWindow"]] = None,
                 location: Optional[Union["Room", List["Room"]]] = None,
                 evaluation: Optional["Evaluation"] = None,
                 announcements: Optional[List[str]] = None):
        self.name = name
        self.qualification = qualification
        self.max_participants = max_participants
        self.tutor = tutor
        self.students = students or []
        self.schedule = schedule or []
        self.location = location
        self.evaluation = evaluation
        self.announcements = announcements or []

    def add_student(self, student: "Student"):
        """
        Add a student to the course, ensuring the maximum limit isn't exceeded.
        """
        if len(self.students) >= self.max_participants:
            logger.warning(f"Cannot add student: Maximum participants ({self.max_participants}) reached.")
            return
        add_student_to_course(student, self)
        self.students.append(student)
        logger.info(f"Student '{student}' added to course '{self.name}'.")
