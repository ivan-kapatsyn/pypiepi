from typing import List
from markdown import markdown

from src.backend.user import User
from src.ui.forms.login_form import LoginForm
from src.utils.path_util import PathUtil
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, render_template_string, \
    send_from_directory


class LoginRoutes:
    main_bp = Blueprint('login', __name__, url_prefix='/login')

    @staticmethod
    @main_bp.route('/process_suggestion', methods=['GET', 'POST'])
    def process_suggestion():
        suggestion = request.json

        user = User.get_user_by_id(suggestion['user_id'])
        user_type = user.user_type

        redirect_url = url_for(f'{user_type}.personal_bio', user_id=suggestion['user_id'])
        return jsonify({'redirect': redirect_url})

    @staticmethod
    @main_bp.route('/get_suggestions', methods=['GET', 'POST'])
    def get_suggestions():
        query = request.args.get('query', '')
        if query:
            suggestions: List[User] = User.search_saved_users(query)
        else:
            suggestions = []
        return jsonify([{
            'username': user.username,
            'user_id': user.user_id
        } for user in suggestions])

    @staticmethod
    @main_bp.route('/index', methods=['GET', 'POST'])
    def index():
        form = LoginForm()
        if request.method == 'POST':
            if form.submit.data and form.validate_on_submit():
                username = form.username.data
                password = form.password.data
                user = User.authenticate(username, password)
                if user is not None:
                    return redirect(url_for(f'{user.user_type}.personal_bio', user_id=user.user_id))
                else:
                    flash('Invalid username or password', 'danger')
            if form.register_new_user.data:
                return redirect(url_for('register.new_user'))
            if form.readme.data:
                return redirect(url_for('login.readme'))
        login_page = r'login.html'
        return render_template(login_page, form=form)

    @staticmethod
    @main_bp.route('/readme', methods=['GET'])
    def readme():
        with open(f"{PathUtil.get_project_path()}/README.md", "r", encoding="utf-8") as f:
            md_content = f.read()

        html_content = markdown(md_content)
        return render_template_string(f"<html><body>{html_content}</body></html>")

    @staticmethod
    @main_bp.route('/config_files/<path:filename>')
    def serve_config_files(filename):
        return send_from_directory(f'{PathUtil.get_project_path()}/config_files', filename)
