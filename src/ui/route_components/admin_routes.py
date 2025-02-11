from flask import Blueprint, render_template, request, jsonify, Response
from numpy import number

from src.backend.course import Course
from src.backend.user import User

# from src.backend.plotting import generate_plot

from src.ui.forms.room_overview import RoomOverview
from src.ui.forms.token_generator import TokenGenerator

import io
import base64
import pandas as pd
import matplotlib.pyplot as plt
from src.backend.user_chart import get_all_registrations_per_week



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
        day = request.args.get('day', 'Mon')
        hour = request.args.get('hour', '9')
        room_form = RoomOverview()
        room_form.day.data = day
        room_form.hour.data = hour
        room_data = AdminRoutes.__get_room_data(day, hour)
        plot_data = AdminRoutes.__generate_plot()
        token_form = TokenGenerator()
        personal_bio_page = r'admin_personal_info.html'
        return render_template(personal_bio_page, username=admin.username,
                               user_id=user_id, remember_me=admin.remember_me,
                               data=data, room_form=room_form,room_data=room_data, token_form=token_form, plot_data=plot_data,)

    @staticmethod
    @main_bp.route('<user_id>/save_token', methods=['POST'])
    def save_token(user_id: str):
        # TODO Replace it with Admin.get_user_by_id()
        admin = User.get_user_by_id(user_id)
        token_form = TokenGenerator()
        if token_form.validate_on_submit():
            user_type = token_form.user_type.data
            token = token_form.token.data
            # Todo Replace it with admin.add_token(Token(user_type, number))
            print(f'{user_type}, {token}')
        return Response(status=204)

    @classmethod
    def __get_room_data(cls, day ='Mon', hour='9'):
        courses = Course.get_courses_by_schedule(day, hour)
        room_data = {
            course.room.room_id: course.course_id for course in courses
        }
        return room_data

    @staticmethod
    def __generate_plot():
        # Holen der aggregierten Registrierungsdaten (Liste von Tupeln: (Week, Total))
        data = get_all_registrations_per_week()

        # Erstelle ein DataFrame aus den Daten
        df = pd.DataFrame(data, columns=['Week', 'Total'])

        # Falls nötig, stelle sicher, dass die 'Week'-Spalte als Datetime interpretiert wird
        df['Week'] = pd.to_datetime(df['Week'])

        # Erstellen des Plots
        plt.figure(figsize=(10, 6))

        # Verwende formatierten Datumsstrings als x-Achse
        plt.bar(df['Week'].dt.strftime("%Y-%m-%d"), df['Total'], color='#0d94b0')

        plt.xlabel('Week (Monday)')
        plt.ylabel('Total Registered Users')
        plt.title('Registrations per Week')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Den Plot in einen BytesIO-Puffer speichern
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # Den Puffer in einen Base64-String kodieren
        plot_data = base64.b64encode(buf.getvalue()).decode('utf8')

        return plot_data
