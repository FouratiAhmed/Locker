from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField 
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from smartLocker.models import User, User2

class typeChoiceForm(FlaskForm):
    delivery = BooleanField ('Delivery Man')
    customer = BooleanField ('Customer')
    next = SubmitField ('Fill Form') 

class registrationForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired(),Length(min=2,max=20)])
    email = StringField('Email', validators = [DataRequired(),Email()])
    address = StringField('address', validators = [DataRequired()])
    password = PasswordField ('Password', validators = [DataRequired(),Length(min=2)])
    confirm_password = PasswordField ('Confirm Password', validators = [DataRequired(),Length(min=2,max=20),EqualTo('password')])
    submit = SubmitField ('Sign Up')
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class registrationDeliveryForm(FlaskForm):
    surname = StringField('Username', validators = [DataRequired(),Length(min=2,max=20)])
    mail_address = StringField('Email', validators = [DataRequired(),Email()])
    password = PasswordField ('Password', validators = [DataRequired(),Length(min=2)])
    confirm_password = PasswordField ('Confirm Password', validators = [DataRequired(),Length(min=2,max=20),EqualTo('password')])
    has_moto = BooleanField ('Has Moto')
    has_car = BooleanField ('Has Car')
    submit = SubmitField ('Sign Up')
    def validate_username(self, surname):
        user = User2.query.filter_by(surname=surname.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, mail_address):
        user = User2.query.filter_by(mail_address=mail_address.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
        
class PinPadForm(FlaskForm):
    lognum = StringField ('Password', validators = [DataRequired(),Length(min=4,max=4)])
    open = SubmitField ('Open')

class LoginForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(),Email()])
    password = PasswordField ('Password', validators = [DataRequired(),Length(min=2,max=20)])
    remember = BooleanField ('Remember Me')
    submit = SubmitField ('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired(),Length(min=2,max=20)])
    email = StringField('Email', validators = [DataRequired(),Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField ('Update')
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
            

class PostForm(FlaskForm):
    title = StringField('Title', validators = [DataRequired()])
    content = TextAreaField('Content', validators = [DataRequired()])
    submit = SubmitField ('Post')