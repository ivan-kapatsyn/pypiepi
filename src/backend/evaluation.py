from datetime import datetime
from typing import List
import logging
from src.utils.data_base_util import DataBaseUtil

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Evaluation:
    def __init__(self, evaluation_id: str, course_id: str, author_id: str, date: datetime,
                 feedback: str, grade: float):
        self.evaluation_id = evaluation_id
        self.course_id = course_id
        self.author_id = author_id
        self.date = date
        self.feedback = feedback
        self.grade = grade

    @staticmethod
    def get_evaluations_by_course_ids(course_ids: List[str]) -> List["Evaluation"]:
        """
        Retrieves all evaluations associated with specific courses.

        Args:
            course_ids List[str]: The unique IDs of the courses.

        Returns:
            List[Evaluation]: A list of Announcement instances associated with the course.
        """
        db = DataBaseUtil()
        try:
            placeholders = ', '.join(['%s'] * len(course_ids))
            evaluation_data = db.load_many("evaluation", f"course_id IN ({placeholders})", course_ids)

            return [
                Evaluation(
                    evaluation_id=data[0],
                    course_id=data[1],
                    author_id=data[2],
                    date=data[3],
                    feedback=data[4],
                    grade=data[5],
                )
                for data in evaluation_data
            ]

        except Exception as e:
            logger.error(f"Error retrieving evaluations for course IDs '{[course_ids]}': {e}")
            return []
