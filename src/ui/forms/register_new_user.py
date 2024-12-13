from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


class RegisterNewUser(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    name = StringField('First name', validators=[DataRequired(), Length(min=4, max=25)])
    surname = StringField('Last name', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Enter your password', validators=[DataRequired()])
    submit = SubmitField('Create')