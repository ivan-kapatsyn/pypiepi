from flask import Blueprint, render_template, Response

from src.backend.user import Tutor, User


class TutorRoutes:
    main_bp = Blueprint('tutor', __name__, url_prefix='/tutor')

    @staticmethod
    @main_bp.route('/<user_id>/personal_bio', methods=['GET', 'POST'])
    def personal_bio(user_id: str):
        # TODO make Tutor.get_user_by_id() work
        tutor = User.get_user_by_id(user_id)
        personal_bio_page = r'tutor_personal_info.html'
        return render_template(personal_bio_page, username=tutor.username, user_id=user_id)

    @staticmethod
    @main_bp.route('/<user_id>/toggle_remeber_me', methods=['GET', 'POST'])
    def toggle_remeber_me(user_id: str):
        user = User.get_user_by_id(user_id)
        # TODO uncomment this code
        # user.toggle_remeber_me()
        return Response(status=204)