from flask import Blueprint, render_template, request, redirect, url_for, flash

from src.backend.admin import Admin
from src.backend.exceptions import DuplicationError, WrongTokenError
from src.backend.qualification import Qualification
from src.backend.student import Student
from src.backend.tutor import Tutor
from src.ui.forms.register_new_user import RegisterNewUser


class RegisterRoutes:
    main_bp = Blueprint('register', __name__, url_prefix='/register')

    @staticmethod
    @main_bp.route('/new_user', methods=['GET', 'POST'])
    def new_user():
        register_page = r'register.html'
        form = RegisterNewUser()
        if form.validate_on_submit():
            data = form.data
            del data['csrf_token']
            del data['submit']
            # Process form data
            user_type = data['user_type']
            del data['user_type']
            additional_info = {}

            if user_type == 'student':
                try:
                    additional_info['token'] = int(request.form.get('student_info_1'))
                except ValueError as e:
                    flash(str(e), 'danger')
                    return render_template(register_page, form=form, error_message="Token has to be a number")
                additional_info['study_program'] = request.form.get('student_info_2')
                data = {**data, **additional_info}
                user_id = Student.register_new_user(**data)
            elif user_type == 'tutor':
                try:
                    additional_info['token'] = int(request.form.get('tutor_info_1'))
                except ValueError as e:
                    flash(str(e), 'danger')
                    return render_template(register_page, form=form, error_message="Token has to be a number")
                additional_info['qualifications'] = request.form.getlist('tutor_info_2[]')
                if len(additional_info['qualifications']) == 0 and additional_info['qualifications'][0] == '':
                    additional_info['qualifications'] = []
                else:
                    additional_info['qualifications'] = [Qualification(name) for name in additional_info['qualifications']]
                data = {**data, **additional_info}
                try:
                    user_id = Tutor.register_new_user(**data)
                except DuplicationError as e:
                    flash(str(e), 'danger')
                    return render_template(register_page, form=form, error_message=str(e))
                except WrongTokenError as e:
                    flash(str(e), 'danger')
                    return render_template(register_page, form=form, error_message=str(e))
            elif user_type == 'admin':
                try:
                    additional_info['token'] = int(request.form.get('admin_info_1'))
                except ValueError as e:
                    flash(str(e), 'danger')
                    return render_template(register_page, form=form, error_message="Token has to be a number")
                additional_info['role'] = request.form.get('admin_info_2')
                data = {**data, **additional_info}
                user_id = Admin.register_new_user(**data)
            return redirect(url_for(f'{user_type}.personal_bio', user_id=user_id))


        return render_template(register_page, form=form)
