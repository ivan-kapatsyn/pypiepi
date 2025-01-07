from flask import Blueprint, render_template, Response, request, jsonify

from src.backend.user import Tutor, User


class TutorRoutes:
    TIMETABLE_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    TIMETABLE_TIME = [f"{hour}AM" if hour < 12 else (f"{hour - 12}PM" if hour > 12 else "12PM") for hour in range(9, 19)]

    main_bp = Blueprint('tutor', __name__, url_prefix='/tutor')

    @staticmethod
    @main_bp.route('/<user_id>/personal_bio', methods=['GET', 'POST'])
    def personal_bio(user_id: str):
        tutor = Tutor.get_user_by_id(user_id)
        courses = tutor.active_courses
        # Todo get courses from tutor
        courses = [
            {"name": "Meeting", "day": "Monday", "time": "9AM", "url": f"/meeting"},
            {"name": "Code Review", "day": "Tuesday", "time": "10AM", "url": "/code-review"},
            {"name": "Standup", "day": "Wednesday", "time": "11AM", "url": "/standup"},
            # Add more events as needed
        ]
        # Todo get data from dict(tutor)
        data = [
            {"name": "Name", "value": tutor.username},
            {"name": "First Name", "value": tutor.first_name},

        ]

        personal_bio_page = r'tutor_personal_info.html'
        return render_template(personal_bio_page, username=tutor.username,
                               user_id=user_id,
                               data = data,
                               events=courses,
                               days=TutorRoutes.TIMETABLE_DAYS, time=TutorRoutes.TIMETABLE_TIME)

    @staticmethod
    @main_bp.route('/<user_id>/toggle_remember_me', methods=['GET', 'POST'])
    def toggle_remember_me(user_id: str):
        user = User.get_user_by_id(user_id)
        user.toggle_saved_button()
        return Response(status=204)

    @staticmethod
    @main_bp.route('/<user_id>/update-data', methods=['GET', 'POST'])
    def update_data(user_id: str):
        try:
            success = True
            tutor = Tutor.get_user_by_id(user_id)
            # Todo enable updating the user
            suggestion = request.json
            info_to_update = suggestion["info_to_update"]
            print(info_to_update)

        except Exception as e:
            success = False
            raise e
        finally:
            status = 204 if success else 500
            return jsonify(success=success), status