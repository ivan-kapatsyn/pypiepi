from flask import Blueprint, Response

from src.backend.user import User


class UserRoutes:
    main_bp = Blueprint('user', __name__, url_prefix='/user')

    @staticmethod
    @main_bp.route('/<user_id>/toggle_remember_me', methods=['GET', 'POST'])
    def toggle_remember_me(user_id: str):
        user = User.get_user_by_id(user_id)
        user.toggle_remember_me()
        return Response(status=204)
