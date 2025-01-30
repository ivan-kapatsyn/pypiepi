from datetime import datetime, timedelta
from typing import List

from flask import Blueprint, Response, render_template, request, redirect, url_for

from src.backend.course import Course
from src.backend.evaluation import Evaluation
from src.backend.tutor import Tutor
from src.backend.user import User
from src.ui.forms.create_new_course import CourseCreationForm


class CoursesRoutes:
    main_bp = Blueprint('course', __name__, url_prefix='/course')

    @staticmethod
    @main_bp.route('/new/<user_id>/', methods=['GET', 'POST'])
    def create_new_course(user_id: str):
        tutor = Tutor.get_user_by_id(user_id)
        form = CourseCreationForm()
        form.qualification.choices = [(value, value) for value in tutor.qualifications]
        if request.method == 'POST':
            if form.submit.data and form.validate_on_submit():
                course_name = form.course_name.data
                qualification = form.qualification.data

                room = form.room.data
                schedule = form.schedule.data
                max_participants = form.max_participants.data
                # Todo Add Course.add_new_course()
                course_id = 1
                return redirect(url_for('course.info', user_id=tutor.user_id, course_id=course_id))

        page = r'create_new_course.html'
        return render_template(page, form=form, tutor_name=tutor.first_name,
                               tutor_surname=tutor.last_name, username=tutor.username,
                               user_id=user_id, remember_me=tutor.remember_me)

    @staticmethod
    @main_bp.route('/info/<course_id>/<user_id>')
    def info(user_id: str, course_id: str):
        user = User.get_user_by_id(user_id)
        course = Course.get_course_by_id(course_id)
        student_list = [
            User.get_user_by_id('430112d4d154a44f'),
            User.get_user_by_id('a76d22eb46a882d2'),
            User.get_user_by_id('903d839e277ca6b9'),
            User.get_user_by_id('99b92b9c4c483607')
        ]
        # Todo replace with course.evaluations
        evaluations = Tutor.get_user_by_id(course.user_id).evaluations
        # Todo add user_type to the User
        user_type = 'Student'
        if user_type == 'Tutor':
            page = 'course_info_tutor.html'
        elif user_type == 'Student':
            #TODO Replace with if user_id in [x.user_id for x in course.student]:
            active_student = True
            if active_student:
                page = 'course_info_active_student.html'
            else:
                page = 'course_info_non_active_student.html'
        else:
            # Todo implement later
            page = '...'
        return render_template(page, user_id=user_id,
                               course_id=course_id,
                               username=user.username,
                               remember_me=user.remember_me,
                               course_data=CoursesRoutes.__construct_course_data(course),
                               students_list=CoursesRoutes.__construct_student_data(student_list),
                               average_rating=CoursesRoutes.__get_average_evaluation(evaluations),
                               feedback_list=CoursesRoutes.__construct_feedback_data(evaluations),
                               announcements=course.announcements
                               )

    @staticmethod
    @main_bp.route('/delete_course/<course_id>/<user_id>')
    def delete_course(course_id: str, user_id: str):
        Course.get_course_by_id(course_id).delete_course()
        return redirect(url_for('tutor.personal_bio', user_id=user_id))

    @staticmethod
    @main_bp.route('/add_announcement/<course_id>/', methods=['POST'])
    def add_announcement(course_id: str):
        # Todo an announcement in db by Course.get_course_by_id() and Course.update()
        message = request.json['message']
        return Response(status=204)

    @staticmethod
    def __construct_course_data(course: Course):
        course_data = {
            'Course name': course.name,
            'Qualification': course.qualification.name,
            'Tutor': Tutor.get_user_by_id(course.user_id).first_name + ' ' + Tutor.get_user_by_id(course.user_id).last_name,
            'Room': course.room.name,
            'Schedule': course.schedule,
            'Max participants': course.max_participants,
            #Todo replace it with course.max_participants - len(course.students)
            'Available seats': course.max_participants - 16
        }
        course_data = [{
            'name': key,
            'value': val
        } for key, val in course_data.items()]
        return course_data

    @staticmethod
    def __construct_student_data(students: List[User]):
        # Todo replace it when Student is implemented
        result = []
        for i, student in enumerate(students):
            result.append({
                'i': i + 1,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'study_program': "Some study program",
            })
        return result

    @staticmethod
    def __get_average_evaluation(evaluation: List[Evaluation]):
        if len(evaluation) == 0:
            return None
        return sum([x.numeric_evaluation for x in evaluation]) / len(evaluation)

    @staticmethod
    def __construct_feedback_data(feedbacks: List[Evaluation]):
        # Todo replace it when Student is implemented
        result = []
        for i, feedback in enumerate(feedbacks):
            result.append({
                'i': i + 1,
                'rating': feedback.numeric_evaluation,
                'name': feedback.author.first_name + ' ' + feedback.author.last_name,
                'date': feedback.date.strftime("%d.%m.%Y %H:%M:%S"),
                'comment': feedback.feedback,
            })
        return result
