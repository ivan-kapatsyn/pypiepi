from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired, NumberRange


class CourseCreationForm(FlaskForm):
    course_name = StringField('Course Name', validators=[DataRequired()])
    qualification = SelectField('Qualification', validators=[DataRequired()], choices=[])
    room = StringField('Room', validators=[DataRequired()])
    schedule = TextAreaField('Schedule (the format is "Mon 9AM". If you want to add more hours add them in a separate line)', validators=[DataRequired()])
    max_participants = IntegerField('Total number of students', validators=[
        DataRequired(),
        NumberRange(min=5, message="There should be more than 5 students."),
        NumberRange(max=40, message="There should be less than 30 students in the class.")
    ])
    submit = SubmitField('Create')
