from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired


class RoomOverview(FlaskForm):
    day = SelectField(
        'Day',
        choices=[
            ('Mon', 'Monday'),
            ('Tue', 'Tuesday'),
            ('Wed', 'Wednesday'),
            ('Thu', 'Thursday'),
            ('Fri', 'Friday'),
        ],
        validators=[DataRequired()]
    )
    hour = SelectField(
        label='Hour',
        choices=[
            ('9', '9:00'),
            ('10', '10:00'),
            ('11', '11:00'),
            ('12', '12:00'),
            ('13', '13:00'),
            ('14', '14:00'),
            ('15', '15:00'),
            ('16', '16:00'),
            ('17', '17:00'),
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Check the rooms')
