from flask import Blueprint, redirect, url_for


class StudentRoutes:
    main_bp = Blueprint('student', __name__, url_prefix='/student')

    @staticmethod
    @main_bp.route('/register_for_course/<course_id>/<user_id>')
    def register_for_course(course_id: str, user_id: str):
        # Todo add user_id to the course in db
        return redirect(url_for('course.info', course_id=course_id, user_id=user_id))
