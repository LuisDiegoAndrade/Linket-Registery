from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class SignUpForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=3, max=66)])
    email = StringField('email', validators=[DataRequired(), Email()] )
    password = PasswordField('password', validators=[DataRequired() ])
    confirm_password = PasswordField('confirm password', validators=[DataRequired(),
                                                       EqualTo('password') ])
    submit = SubmitField('sign up')


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()] )
    password = PasswordField('password', validators=[DataRequired(), Length(min=3, max=66)] )
    #remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')
