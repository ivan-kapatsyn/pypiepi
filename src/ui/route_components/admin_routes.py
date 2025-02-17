from flask import Blueprint, render_template, request, jsonify, Response
from numpy import number

from src.backend.admin import Admin
from src.backend.course import Course
from src.backend.user import User


from src.ui.forms.room_overview import RoomOverview
from src.ui.forms.token_generator import TokenGenerator

import io
import base64
import pandas as pd
import matplotlib.pyplot as plt
from src.backend.user_chart import get_all_registrations_per_week


class AdminRoutes:
    # Days of the week for the timetable
    TIMETABLE_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    # Time slots from 9 AM to 6 PM
    TIMETABLE_TIME = [f"{hour}AM" if hour < 12 else (f"{hour - 12}PM" if hour > 12 else "12PM") for hour in
                      range(9, 19)]

    # Blueprint for the '/admin' routes
    main_bp = Blueprint('admin', __name__, url_prefix='/admin')

    @staticmethod
    @main_bp.route('/<user_id>/personal_bio', methods=['GET', 'POST'])
    def personal_bio(user_id: str):
        # Fetch user data based on user_id
        admin = Admin.get_user_by_id(user_id)

        # Prepare data to display in the personal bio section
        data = [
            {"name": "Username", "value": admin.username},
            {"name": "First Name", "value": admin.first_name},
            {"name": "Last Name", "value": admin.last_name},
            {"name": "Bio", "value": admin.bio},
            {"name": "Role", "value": admin.role}
        ]

        # Get query parameters for day and hour, default to Monday and 9AM
        day = request.args.get('day', 'Mon')
        hour = request.args.get('hour', '9')

        # Initialize forms
        room_form = RoomOverview()
        room_form.day.data = day
        room_form.hour.data = hour

        # Get the room data for the selected day and hour
        room_data = AdminRoutes.__get_room_data(day, hour)

        # Generate a plot (for registered users per week)
        plot_data = AdminRoutes.__generate_plot()

        # Token generation form
        token_form = TokenGenerator()

        # Render the template with the gathered data
        personal_bio_page = r'admin_personal_info.html'
        return render_template(personal_bio_page, username=admin.username,
                               user_id=user_id, remember_me=admin.remember_me,
                               data=data, room_form=room_form,room_data=room_data, token_form=token_form, plot_data=plot_data,)

    @staticmethod
    @main_bp.route('/<user_id>/update-data', methods=['GET', 'POST'])
    def update_data(user_id: str):
        try:
            success = True
            admin = Admin.get_user_by_id(user_id)
            suggestion = request.json
            info_to_update: dict = suggestion["info_to_update"]
            key_list = info_to_update.keys()
            temp = {}
            for key in key_list:
                temp[key.lower().replace(' ', '_')] = info_to_update[key]
            info_to_update = temp

            # Update the user data
            admin.update_user_values(info_to_update)

        except Exception as e:
            success = False
            raise e
        finally:
            # Return a response based on success or failure
            status = 204 if success else 500
            return jsonify(success=success), status

    @staticmethod
    @main_bp.route('<user_id>/save_token', methods=['POST'])
    def save_token(user_id: str):
        # Retrieve the admin user by user_id
        admin = Admin.get_user_by_id(user_id)

        # Validate the token generation form and save the token
        token_form = TokenGenerator()
        if token_form.validate_on_submit():
            token = token_form.token.data
            admin.add_token(token)

        # Respond with a success status (no content returned)
        return Response(status=204)

    @classmethod
    def __get_room_data(cls, day='Mon', hour='9'):
        # Fetch courses based on the selected day and hour
        courses = Course.get_courses_by_schedule(day, hour)

        # Create a dictionary mapping room IDs to course IDs
        room_data = {
            course.room.room_id: course.course_id for course in courses
        }
        return room_data

    @staticmethod
    def __generate_plot():
        # Retrieve all user registration data per week
        data = get_all_registrations_per_week()

        # Create a DataFrame from the registration data
        df = pd.DataFrame(data, columns=['Week', 'Total'])

        # Ensure 'Week' is interpreted as a datetime type
        df['Week'] = pd.to_datetime(df['Week'])

        # Create the plot with matplotlib
        plt.figure(figsize=(10, 6))
        plt.bar(df['Week'].dt.strftime("%Y-%m-%d"), df['Total'], color='#0d94b0')

        # Set labels and title for the plot
        plt.xlabel('Week (starting from Monday)')
        plt.ylabel('Total Registered Users')
        plt.title('Overall registrations')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save the plot to a BytesIO buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # Convert the buffer to a base64 string and return it
        plot_data = base64.b64encode(buf.getvalue()).decode('utf8')
        return plot_data
