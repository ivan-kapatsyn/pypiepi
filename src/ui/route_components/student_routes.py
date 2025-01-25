from flask import Blueprint


class StudentRoutes:
    main_bp = Blueprint('student', __name__, url_prefix='/student')