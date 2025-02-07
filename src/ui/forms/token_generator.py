from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import IntegerRangeField, IntegerField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, NumberRange


class TokenGenerator(FlaskForm):
    user_type = SelectField(
        'User Type',
        choices=[('student', 'Student'), ('tutor', 'Tutor'), ('admin', 'Admin')],
        validators=[DataRequired()]
    )
    token = IntegerField(
        label='Enter new token',
        validators=[
            DataRequired(),
            NumberRange(min=100000000, message="There should be more than 9 numbers"),
            NumberRange(max=1000000000, message="There should be less than 10 numbers")
        ]
    )
    submit = SubmitField('Create')