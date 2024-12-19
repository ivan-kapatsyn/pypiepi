
from flask import Blueprint, render_template, request

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
            elif usertype == 'tutor':
                additional_info['tutor_register_number'] = request.form.get('tutor_info_1')
                additional_info['qualifications'] = request.form.getlist('tutor_info_2[]')
                if len(additional_info['qualifications']) == 0 and additional_info['qualifications'][0] == '':
                    additional_info['qualifications'] = []
            elif usertype == 'admin':
                additional_info['admin_info_1'] = request.form.get('admin_info_1')
                additional_info['admin_info_2'] = request.form.get('admin_info_2')
                additional_info['admin_info_3'] = request.form.get('admin_info_3')

            # Todo use Tutor.register_new_user()
            print(f"Usertype: {usertype}, Additional Info: {additional_info}")
            # Todo Render a new page
            return "Form Submitted Successfully!"

        register_page = r'register.html'
        return render_template(register_page, form=form)