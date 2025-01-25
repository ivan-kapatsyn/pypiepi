from datetime import datetime

from flask import Blueprint, redirect, url_for, request, jsonify

from src.backend.evaluation import Evaluation
from src.backend.user import User


class StudentRoutes:
    main_bp = Blueprint('student', __name__, url_prefix='/student')

    @staticmethod
    @main_bp.route('/register_for_course/<course_id>/<user_id>')
    def register_for_course(course_id: str, user_id: str):
        # Todo add user_id to the course in db
        return redirect(url_for('course.info', course_id=course_id, user_id=user_id))

    @staticmethod
    @main_bp.route('/leave_feedback/<course_id>/<user_id>', methods=['GET', 'POST'])
    def leave_feedback(course_id: str, user_id: str):
        rating = request.json.get('rating', '')
        feedback = request.json.get('feedback', '')
        evaluation = Evaluation(
            evaluation_id='1',
            author=User.get_user_by_id(user_id),
            date=datetime.now(),
            numeric_evaluation=int(rating),
            feedback=feedback,
        )
        #Todo save evaluation to the db
        return jsonify({
            'name': evaluation.author.first_name + ' ' + evaluation.author.last_name,
            'date': evaluation.date.strftime("%d.%m.%Y %H:%M:%S"),
            'grade': evaluation.numeric_evaluation,
            'message': evaluation.feedback,
        })
