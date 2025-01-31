from datetime import datetime
from typing import List

from flask import Blueprint, redirect, url_for, request, jsonify, render_template

from src.backend.course import Course
from src.backend.evaluation import Evaluation
from src.backend.user import User


class StudentRoutes:
    TIMETABLE_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    TIMETABLE_TIME = [f"{hour}AM" if hour < 12 else (f"{hour - 12}PM" if hour > 12 else "12PM") for hour in
                      range(9, 19)]

    main_bp = Blueprint('student', __name__, url_prefix='/student')

    @staticmethod
    @main_bp.route('/register_for_course/<course_id>/<user_id>')
    def register_for_course(course_id: str, user_id: str):
        # Todo add user_id to the course in db
        return redirect(url_for('course.info', course_id=course_id, user_id=user_id))

    @staticmethod
    @main_bp.route('/drop_course/<course_id>/<user_id>')
    def drop_course(course_id: str, user_id: str):
        # Todo remove user_id from the course in db
        return redirect(url_for('student.personal_bio', user_id=user_id))

    @staticmethod
    @main_bp.route('/leave_feedback/<course_id>/<user_id>', methods=['GET', 'POST'])
    def leave_feedback(course_id: str, user_id: str):
        rating = request.json.get('rating', '')
        feedback = request.json.get('feedback', '')
        evaluation = Evaluation(
            evaluation_id='1',
            author=User.get_user_by_id(user_id),
            date=datetime.now(),
            numeric_evaluation=int(rating),
            feedback=feedback,
        )
        # Todo save evaluation to the db
        return jsonify({
            'name': evaluation.author.first_name + ' ' + evaluation.author.last_name,
            'date': evaluation.date.strftime("%d.%m.%Y %H:%M:%S"),
            'grade': evaluation.numeric_evaluation,
            'message': evaluation.feedback,
        })

    @staticmethod
    @main_bp.route('/<user_id>/personal_bio', methods=['GET', 'POST'])
    def personal_bio(user_id: str):
        # TODO Replace it with Student when it's ready
        student = User.get_user_by_id(user_id)
        active_courses: List[Course] = [
            Course.get_course_by_id(course_id='dc295cc4dd09d5b1')
        ]
        courses = [{
            "name": course.name,
            "day": StudentRoutes.__get_day_from_schedule(course.schedule),
            "time": StudentRoutes.__get_start_time_from_schedule(course.schedule),
            "url": url_for('course.info', user_id=student.user_id, course_id=course.course_id)
            # TODO Replace with student.active_courses
        } for course in active_courses]

        data = [
            {"name": "Username", "value": student.username},
            {"name": "First Name", "value": student.first_name},
            {"name": "Last Name", "value": student.last_name},
            {"name": "Bio", "value": student.bio},
            {"name": "Study program",
             # TODO replace value with student.study_program
             "value": 'Data Science'
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
            # TODO replace with Student
            tutor = User.get_user_by_id(user_id)
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
        # Todo obtain courses by student.get_active_courses()
        courses = [
            Course.get_course_by_id(course_id='dc295cc4dd09d5b1'),
            Course.get_course_by_id(course_id='39104442b2660b56'),
            Course.get_course_by_id(course_id='f61985b87284171a'),
        ]

        search_query = request.args.get('search', '')
        courses = [course for course in courses if course.name.lower().startswith(search_query.lower())]
        return StudentRoutes.__render_search_page(user_id, search_query, courses,True)

    @staticmethod
    @main_bp.route('/<user_id>/passive-courses', methods=['GET', 'POST'])
    def passive_courses(user_id: str):
        # Todo obtain courses by student.get_active_courses()
        courses = [
            Course.get_course_by_id(course_id='dc295cc4dd09d5b1'),
            Course.get_course_by_id(course_id='39104442b2660b56'),
            Course.get_course_by_id(course_id='f61985b87284171a'),
        ]

        search_query = request.args.get('search', '')
        courses = [course for course in courses if course.name.lower().startswith(search_query.lower())]
        return StudentRoutes.__render_search_page(user_id,search_query, courses, False)

    @staticmethod
    def __render_search_page(user_id, search_query, courses, is_active):
        # Todo Replace it with Student
        student = User.get_user_by_id(user_id)
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
        if int(start_time) < 12 and int(start_time) > 8:
            start_time += 'AM'
        else:
            start_time += 'PM'
        return start_time
