from flask import Blueprint, render_template


class RegisterRoutes:
    main_bp = Blueprint('register', __name__, url_prefix='/register')

    @staticmethod
    @main_bp.route('/new_user', methods=['GET', 'POST'])
    def new_user():
        login_page = r'register.html'
        return render_template(login_page, message="You are being registered")