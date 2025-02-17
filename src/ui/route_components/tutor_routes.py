from typing import List

from flask import Blueprint, render_template, request, jsonify, url_for

from src.backend.course import Course
from src.backend.evaluation import Evaluation
from src.backend.qualification import Qualification
from src.backend.tutor import Tutor
from src.backend.user import User


class TutorRoutes:
    TIMETABLE_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    TIMETABLE_TIME = [i for i in range(9, 19)]

    main_bp = Blueprint('tutor', __name__, url_prefix='/tutor')

    @staticmethod
    @main_bp.route('/<user_id>/personal_bio', methods=['GET', 'POST'])
    def personal_bio(user_id: str):
        tutor = Tutor.get_user_by_id(user_id)
        courses = [{
            "name": course.name,
            "day": TutorRoutes.__get_day_from_schedule(course.schedule),
            "start_time": TutorRoutes.__get_start_time_from_schedule(course.schedule),
            "end_time": TutorRoutes.__get_end_time_from_schedule(course.schedule),
            "url": url_for('course.info', user_id=tutor.user_id, course_id=course.course_id)
        }
            for course in tutor.active_courses]

        data = [
            {"name": "Username", "value": tutor.username},
            {"name": "First Name", "value": tutor.first_name},
            {"name": "Last Name", "value": tutor.last_name},
            {"name": "Bio", "value": tutor.bio},

        ]
        qualification_data = [
            {"name": "qualification_1", "value": qual.name}
        for i, qual in enumerate(tutor.qualifications)]
        qualification_data.append({"name": "qualification_new", "value": ''})
        average_rating, feedbacks = TutorRoutes.__construct_feedback_data(tutor.evaluations)
        personal_bio_page = r'tutor_personal_info.html'
        return render_template(personal_bio_page, username=tutor.username,
                               user_id=user_id, remember_me=tutor.remember_me,
                               data=data, qualification_data=qualification_data,
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
            info_to_update: dict = suggestion["info_to_update"]
            key_list = info_to_update.keys()
            temp = {}
            for key in key_list:
                if 'qualification' in key:
                    qualifications = tutor.qualifications
                    qualification_index_to_update = key.split('_')[-1]
                    if qualification_index_to_update != 'new':
                        qualification_index_to_update = int(qualification_index_to_update) - 1
                        qualifications[qualification_index_to_update] = Qualification(info_to_update[key])
                    else:
                        qualifications.append(info_to_update[key])

                    temp['qualification'] = qualifications
                else:
                    temp[key.lower().replace(' ', '_')] = info_to_update[key]
            info_to_update = temp
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
        return int(start_time)

    @staticmethod
    def __get_end_time_from_schedule(schedule):
        time_window = schedule[3:]
        end_time: str = time_window.split('-')[1]
        end_time = end_time.strip()
        return int(end_time)
