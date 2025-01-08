from flask import Blueprint, Response, render_template, request, redirect, url_for, flash

from src.backend.user import User, Tutor
from src.ui.forms.create_new_course import CourseCreationForm


class CoursesRoutes:
    main_bp = Blueprint('course', __name__, url_prefix='/course')

    @staticmethod
    @main_bp.route('/new/<user_id>/', methods=['GET', 'POST'])
    def create_new_course(user_id: str):
        tutor = Tutor.get_user_by_id(user_id)
        form = CourseCreationForm()
        form.qualification.choices = [(value,value) for value in tutor.qualifications]
        if request.method == 'POST':
            if form.submit.data and form.validate_on_submit():
                course_name = form.course_name.data
                qualification = form.qualification.data

                room = form.room.data
                schedule = form.schedule.data
                max_participants = form.max_participants.data
                # Todo Add Course.add_new_course()
                return redirect(url_for('course.info', user_id=tutor.user_id))

        login_page = r'create_new_course.html'
        return render_template(login_page, form=form, tutor_name=tutor.first_name,
                               tutor_surname=tutor.last_name)
