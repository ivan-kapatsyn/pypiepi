from flask import Blueprint, render_template, request, redirect, url_for

from src.backend.tutor import Tutor
from src.ui.forms.register_new_user import RegisterNewUser


class RegisterRoutes:
    main_bp = Blueprint('register', __name__, url_prefix='/register')

    @staticmethod
    @main_bp.route('/new_user', methods=['GET', 'POST'])
    def new_user():
        form = RegisterNewUser()
        if form.validate_on_submit():
            # Process form data
            usertype = request.form.get('usertype')
            additional_info = {}

            if usertype == 'student':
                additional_info['student_info'] = request.form.get('student_info')
                data = {**form.data, **additional_info}
                # TODO add Student.register_new_user()
                user_id = 1
            elif usertype == 'tutor':
                additional_info['tutor_register_number'] = request.form.get('tutor_info_1')
                additional_info['qualifications'] = request.form.getlist('tutor_info_2[]')
                if len(additional_info['qualifications']) == 0 and additional_info['qualifications'][0] == '':
                    additional_info['qualifications'] = []
                data = {**form.data, **additional_info}
                user_id = Tutor.register_new_user(**data)
            elif usertype == 'admin':
                additional_info['admin_info_1'] = request.form.get('admin_info_1')
                additional_info['admin_info_2'] = request.form.get('admin_info_2')
                additional_info['admin_info_3'] = request.form.get('admin_info_3')
                data = {**form.data, **additional_info}
                # TODO add Admin.register_new_user()
                user_id = 1
            return redirect(url_for(f'{usertype}.personal_bio', user_id=user_id))

        register_page = r'register.html'
        return render_template(register_page, form=form)
