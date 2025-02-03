from flask import Blueprint, render_template, request

from src.backend.user import User
from src.ui.forms.room_overview import RoomOverview


class AdminRoutes:
    TIMETABLE_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    TIMETABLE_TIME = [f"{hour}AM" if hour < 12 else (f"{hour - 12}PM" if hour > 12 else "12PM") for hour in
                      range(9, 19)]

    main_bp = Blueprint('admin', __name__, url_prefix='/admin')

    @staticmethod
    @main_bp.route('/<user_id>/personal_bio', methods=['GET', 'POST'])
    def personal_bio(user_id: str):
        # TODO Replace it with Admin.get_user_by_id()
        admin = User.get_user_by_id(user_id)
        data = [
            {"name": "Username", "value": admin.username},
            {"name": "First Name", "value": admin.first_name},
            {"name": "Last Name", "value": admin.last_name},
            {"name": "Bio", "value": admin.bio},
            {"name": "Role", "value": "Senior Administrator"}
        ]
        form = RoomOverview()
        if request.method == 'POST':
            if form.submit.data and form.validate_on_submit():
                day = form.day.data
                hour = form.hour.data

        personal_bio_page = r'admin_personal_info.html'
        return render_template(personal_bio_page, username=admin.username,
                               user_id=user_id, remember_me=admin.remember_me,
                               data=data, form=form)