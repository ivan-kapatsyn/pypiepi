from datetime import datetime
from typing import List

from flask import Blueprint, redirect, url_for, request, jsonify, render_template
from pandas.core.computation.expressions import evaluate

from src.backend.course import Course
from src.backend.evaluation import Evaluation
from src.backend.student import Student
from src.backend.user import User
from src.utils.data_base_util import DataBaseUtil
from tests.backend.data_base_util import DataBaseUtilTestCase


class StudentRoutes:
    TIMETABLE_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    TIMETABLE_TIME = [i for i in range(9, 19)]

    main_bp = Blueprint('student', __name__, url_prefix='/student')

    @staticmethod
    @main_bp.route('/register_for_course/<course_id>/<user_id>', methods=['GET', 'POST'])
    def register_for_course(course_id: str, user_id: str):
        student = Student.get_user_by_id(user_id)
        student.register_for_a_course(course_id)
        return redirect(url_for('course.info', course_id=course_id, user_id=user_id))

    @staticmethod
    @main_bp.route('/drop_course/<course_id>/<user_id>', methods=['GET', 'POST'])
    def drop_course(course_id: str, user_id: str):
        student = Student.get_user_by_id(user_id)
        student.unregister_for_a_course(course_id)
        return redirect(url_for('student.personal_bio', user_id=user_id))

    @staticmethod
    @main_bp.route('/leave_feedback/<course_id>/<user_id>', methods=['GET', 'POST'])
    def leave_feedback(course_id: str, user_id: str):
        rating = request.json.get('rating', '')
        feedback = request.json.get('feedback', '')
        student = Student.get_user_by_id(user_id)
        evaluation_id = student.leave_feedback(course_id, feedback, rating)
        # Todo change it to Evaluation.get_by_id()
        evaluation = DataBaseUtil().load_one('evaluation', evaluation_id)
        return jsonify({
            'name': student.first_name + ' ' + student.last_name,
            # Todo change it to evaluation.date
            'date': evaluation[4].strftime("%d.%m.%Y %H:%M:%S"),
            'grade': rating,
            'message': feedback,
        })

    @staticmethod
    @main_bp.route('/<user_id>/personal_bio', methods=['GET', 'POST'])
    def personal_bio(user_id: str):
        student = Student.get_user_by_id(user_id)
        courses = [{
            "name": course.name,
            "day": StudentRoutes.__get_day_from_schedule(course.schedule),
            "start_time": StudentRoutes.__get_start_time_from_schedule(course.schedule),
            "end_time": StudentRoutes.__get_end_time_from_schedule(course.schedule),
            "url": url_for('course.info', user_id=student.user_id, course_id=course.course_id)
        } for course in student.active_courses]

        data = [
            {"name": "Username", "value": student.username},
            {"name": "First Name", "value": student.first_name},
            {"name": "Last Name", "value": student.last_name},
            {"name": "Bio", "value": student.bio},
            {"name": "Study program", "value": student.study_program
             },

        ]

        return render_template('student_personal_info.html', username=student.username,
                               user_id=user_id, remember_me=student.remember_me,
                               data=data,
                               events=courses,
                               days=StudentRoutes.TIMETABLE_DAYS, times=StudentRoutes.TIMETABLE_TIME)

    @staticmethod
    @main_bp.route('/<user_id>/update-data', methods=['GET', 'POST'])
    def update_data(user_id: str):
        try:
            success = True
            tutor = Student.get_user_by_id(user_id)
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
    @main_bp.route('/<user_id>/active-courses', methods=['GET', 'POST'])
    def active_courses(user_id: str):
        student = Student.get_user_by_id(user_id)
        courses = student.active_courses

        search_query = request.args.get('search', '')
        courses = [course for course in courses if course.name.lower().startswith(search_query.lower())]
        return StudentRoutes.__render_search_page(user_id, search_query, courses, True)

    @staticmethod
    @main_bp.route('/<user_id>/passive-courses', methods=['GET', 'POST'])
    def passive_courses(user_id: str):
        courses = []

        search_query = request.args.get('search', '')
        if search_query != '':
            courses = Course.get_courses_by_name_start(search_query)
        return StudentRoutes.__render_search_page(user_id, search_query, courses, False)

    @staticmethod
    def __render_search_page(user_id, search_query, courses, is_active):
        student = Student.get_user_by_id(user_id)
        return render_template('student_search_courses.html', user_id=user_id, courses=courses,
                               search_query=search_query, username=student.username,
                               remember_me=student.remember_me, is_active=is_active)

    @staticmethod
    def __get_day_from_schedule(schedule):
        day_code = schedule[:3]
        for x in StudentRoutes.TIMETABLE_DAYS:
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
