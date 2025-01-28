from typing import List

from flask import Blueprint, render_template, request, jsonify, url_for

from src.backend.course import Course
from src.backend.evaluation import Evaluation
from src.backend.tutor import Tutor
from src.backend.user import User


class TutorRoutes:
    TIMETABLE_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    TIMETABLE_TIME = [f"{hour}AM" if hour < 12 else (f"{hour - 12}PM" if hour > 12 else "12PM") for hour in
                      range(9, 19)]

    main_bp = Blueprint('tutor', __name__, url_prefix='/tutor')

    @staticmethod
    @main_bp.route('/<user_id>/personal_bio', methods=['GET', 'POST'])
    def personal_bio(user_id: str):
        tutor = Tutor.get_user_by_id(user_id)
        courses = [{
            "name": course.name,
            "day": TutorRoutes.__get_day_from_schedule(course.schedule),
            "time": TutorRoutes.__get_start_time_from_schedule(course.schedule),
            "url": url_for('course.info', user_id=tutor.user_id, course_id=course.course_id)
        }
            for course in tutor.active_courses]
        data = [
            {"name": "Username", "value": tutor.username},
            {"name": "First Name", "value": tutor.first_name},
            {"name": "Last Name", "value": tutor.last_name},
            {"name": "Bio", "value": tutor.bio},
            {"name": "Qualification",
             "value": '\n'.join([f'{i+1}) {qual.name}' for i, qual in enumerate(tutor.qualifications)])},

        ]
        average_rating, feedbacks = TutorRoutes.__construct_feedback_data(tutor.evaluations)
        personal_bio_page = r'tutor_personal_info.html'
        return render_template(personal_bio_page, username=tutor.username,
                               user_id=user_id, remember_me=tutor.remember_me,
                               data=data,
                               events=courses,
                               days=TutorRoutes.TIMETABLE_DAYS, times=TutorRoutes.TIMETABLE_TIME,
                               average_rating=average_rating, feedback_list=feedbacks)

    @staticmethod
    @main_bp.route('/<user_id>/update-data', methods=['GET', 'POST'])
    def update_data(user_id: str):
        try:
            success = True
            tutor = Tutor.get_user_by_id(user_id)
            suggestion = request.json
            info_to_update = suggestion["info_to_update"]
            tutor.update_user_values(info_to_update)

        except Exception as e:
            success = False
            raise e
        finally:
            status = 204 if success else 500
            return jsonify(success=success), status

    @staticmethod
    def __construct_feedback_data(feedbacks: List[Evaluation]):
        result = []
        average = 0
        if len(feedbacks) == 0:
            return None, result
        for i, feedback in enumerate(feedbacks):
            author = User.get_user_by_id(feedback.author_id)
            result.append({
                'i': i + 1,
                'rating': feedback.grade,
                'name': author.first_name + ' ' + author.last_name,
                'comment': feedback.feedback
            })
            average += feedback.grade
        return average / len(feedbacks), result

    @staticmethod
    def __get_day_from_schedule(schedule):
        day_code = schedule[:3]
        for x in TutorRoutes.TIMETABLE_DAYS:
            if day_code in x:
                return x

        return None

    @staticmethod
    def __get_start_time_from_schedule(schedule):
        time_window = schedule[3:]
        start_time: str = time_window.split('-')[0]
        start_time = start_time.strip()
        if int(start_time) < 12 and int(start_time) > 8:
            start_time += 'AM'
        else:
            start_time += 'PM'
        return start_time
