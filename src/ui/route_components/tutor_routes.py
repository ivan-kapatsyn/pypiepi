from flask import Blueprint, render_template

from src.backend.user import Tutor, User


class TutorRoutes:
    main_bp = Blueprint('tutor', __name__, url_prefix='/tutor')

    @staticmethod
    @main_bp.route('/personal_bio/<user_id>', methods=['GET', 'POST'])
    def personal_bio(user_id: int):
        # TODO make Tutor.get_user_by_id() work
        tutor = User.get_user_by_id(str(user_id))
        personal_bio_page = r'tutor_personal_info.html'
        return render_template(personal_bio_page, username=tutor.username)