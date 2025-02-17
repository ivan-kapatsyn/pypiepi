from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import HiddenField
from wtforms.validators import DataRequired, NumberRange

from src.backend.room import Room


class CourseCreationForm(FlaskForm):
    error_message = StringField()
    course_name = StringField('Course Name', validators=[DataRequired()])
    qualification = SelectField('Qualification', validators=[DataRequired()], choices=[])
    room = SelectField(
        label='Room',
        validators=[DataRequired()],
        choices=[(room_instance.room_id, room_instance.name) for room_instance in Room.get_rooms_by_name_prefix('')],
    )
    schedule = TextAreaField('Schedule', validators=[DataRequired()])
    max_participants = IntegerField('Total number of students', validators=[
        DataRequired(),
        NumberRange(min=5, message="There should be more than 5 students."),
        NumberRange(max=40, message="There should be less than 30 students in the class.")
    ])
    submit = SubmitField('Create')
