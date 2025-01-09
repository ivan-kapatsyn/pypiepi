from flask import Blueprint, Response, render_template, request, redirect, url_for, flash

from src.backend.course import Course
from src.backend.evaluation import Evaluation
from src.backend.qualification import Qualification
from src.backend.room import Room
from src.backend.time_window import TimeWindow
from src.backend.user import User, Tutor
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
    def info(user_id: str, course_id: int):
        user = User.get_user_by_id(user_id)
        # Todo retrieve Course by Course.get_course_by_id()
        course = Course(
            name="Mafia 1",
            qualification=Qualification("Math"),
            max_participants=30,
            tutor=user,  # We assume that we will log in from the tutors perspective
            students=[
                ("Lorenz", 'Applied Data Science'),
                ("Sofia", 'Applied Informatics'),
                ("Markus", 'Applied Data Science'),
                ("Lilit", 'Applied Informatics')
            ],
            schedule=[
                TimeWindow(day='Mon', start_time='9AM', end_time='10AM'),
                TimeWindow(day='Thu', start_time='9AM', end_time='10AM')
            ],
            location=Room('Prov.103'),
            evaluation=Evaluation([(8.9, 'it was nice')]),  # Todo specify the structure of Evaluation
            announcements=['Today the class is off']  # Todo add date to the announcement
        )
        # Todo add user_type to the User
        user_type = 'Tutor'
        if user_type == 'Tutor':
            page = 'course_info_tutor.html'
            return render_template(page, user_id=user_id,
                                   course_id=course_id,
                                   username=user.username,
                                   remember_me=user.remember_me,
                                   course_data=CoursesRoutes.__construct_course_data(course),
                                   students_list=CoursesRoutes.__construct_student_data(course.students),
                                   average_rating=CoursesRoutes.__get_average_evaluation(course.evaluation.ratings),
                                   feedback_list=CoursesRoutes.__construct_feedback_data(course.evaluation.ratings),
                                   announcements=course.announcements
                                   )
        elif user_type == 'Student':
            # Todo implement later
            pass
        else:
            # Todo implement later
            pass

    @staticmethod
    @main_bp.route('/delete_course/<course_id>/<user_id>')
    def delete_course(course_id: str, user_id: str):
        # Todo delete course in db
        return redirect(url_for('tutor.personal_bio', user_id=user_id))

    @staticmethod
    @main_bp.route('/add_announcement/<course_id>/', methods=['POST'])
    def add_announcement(course_id: str):
        # Todo an announcement in db by Course.get_course_by_id() and Course.update()
        return Response(status=204)

    @staticmethod
    def __construct_course_data(course: Course):
        course_data = {
            'Course name': course.name,
            'Qualification': course.qualification.name,
            'Tutor': course.tutor.first_name + ' ' + course.tutor.last_name,
            'Room': course.location.name,
            'Schedule': '\n'.join([f'{x.day} {x.start_time}' for x in course.schedule]),
            'Max participants': course.max_participants,
        }
        course_data = [{
            'name': key,
            'value': val
        } for key, val in course_data.items()]
        return course_data

    @staticmethod
    def __construct_student_data(students):
        # Todo replace it when Student is implemented
        result = []
        for i, student in enumerate(students):
            result.append({
                'i': i + 1,
                'first_name': student[0],
                'last_name': 'Surname',
                'study_program': student[1]
            })
        return result

    @staticmethod
    def __get_average_evaluation(evaluation):
        return sum([x[0] for x in evaluation]) / len(evaluation)

    @staticmethod
    def __construct_feedback_data(feedbacks):
        # Todo replace it when Student is implemented
        result = []
        for i, feedback in enumerate(feedbacks):
            result.append({
                'i': i + 1,
                'rating': feedback[0],
                'name': 'Anonymous',
                'comment': feedback[1]
            })
        return result
