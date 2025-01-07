from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class CourseCreationForm(FlaskForm):
    course_name = StringField('Course Name', validators=[DataRequired()])
    qualification = StringField('Qualification', validators=[DataRequired()])
    room = StringField('Room', validators=[DataRequired()])
    schedule = TextAreaField('Schedule (e.g., Mon-Fri 9AM-12PM)', validators=[DataRequired()])
    max_participants = IntegerField('Max Number of Participants', validators=[
        DataRequired(),
        NumberRange(min=1, message="The number must be greater than 0.")
    ])
    submit = SubmitField('Create')
