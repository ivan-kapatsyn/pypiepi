from flask import Blueprint, render_template


class TutorRoutes:
    main_bp = Blueprint('tutor', __name__, url_prefix='/tutor')

    @staticmethod
    @main_bp.route('/personal_bio/<user_id>', methods=['GET', 'POST'])
    def personal_bio(user_id: int):
        personal_bio_page = r'tutor_personal_info.html'
        return render_template(personal_bio_page)