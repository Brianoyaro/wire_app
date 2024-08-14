from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email
from app.models import User
from flask_wtf.file import FileField, FileAllowed


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email():
        user = User.query.filter_by(email=email.data)
        if user is not None:
            raise ValidationError('Email exists')
        

class NewItemForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    # add seller _id when form is posted
    price = FloatField('Price', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image = FileField('Select Item image', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('submit')