from typing import List

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify

from src.backend.user import User
from src.ui.forms.login_form import LoginForm


class Routes(object):
    main_bp = Blueprint('main', __name__)

    @staticmethod
    @main_bp.route('/process_suggestion', methods=['GET', 'POST'])
    def process_suggestion():
        suggestion = request.json

        redirect_url = url_for('main.personal_bio', user_id=suggestion['user_id'])
        return jsonify({'redirect': redirect_url})

    @staticmethod
    @main_bp.route('/get_suggestions', methods=['GET', 'POST'])
    def get_suggestions():
        query = request.args.get('query', '')
        if query:
            suggestions: List[User] = User.search_for_a_saved_users(query)
        else:
            suggestions = []
        return jsonify([{
            'username': user.username,
            'user_id': user.user_id
        }for user in suggestions])

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
    @main_bp.route('/personal_bio/<user_id>')
    def personal_bio(user_id):
        user = User.get_user_by_id(user_id)

        personal_bio_page = r'personal_bio.html'
        # Todo remake bio when implementing Student and Tutor functionality
        return render_template(personal_bio_page, username=user.username, bio=f"This is {user.bio}'s page")
