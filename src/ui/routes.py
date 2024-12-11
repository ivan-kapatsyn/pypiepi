from typing import List

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify

from src.backend.user import User
from src.ui.forms.login_form import LoginForm


class Routes(object):
    main_bp = Blueprint('main', __name__)

    @staticmethod
    @main_bp.route('/get_suggestions', methods=['GET', 'POST'])
    def get_suggestions():
        query = request.args.get('query', '')
        if query:
            suggestions: List[User] = User.search_for_a_saved_users(query)
        else:
            suggestions = []
        return jsonify([user.username for user in suggestions])

    @staticmethod
    @main_bp.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if request.method == 'POST' and form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            if User.authenticate(username, password):
                return redirect(url_for('main.personal_bio', username=username))
            else:
                flash('Invalid username or password', 'danger')
        # TODO extract the path from the utils
        login_page = r'login.html'
        return render_template(login_page, form=form)

    @staticmethod
    @main_bp.route('/personal_bio/<username>')
    def personal_bio(username):
        user = username
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('main.login'))

        # TODO extract the path from the utils
        personal_bio_page = r'personal_bio.html'
        return render_template(personal_bio_page, username=username, bio=user['bio'])
