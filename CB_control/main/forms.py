from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField,
						MultipleFileField)
from wtforms.validators import (DataRequired, Length, Email, EqualTo, ValidationError, InputRequired,
								NumberRange)
from flask_login import current_user
import pytz
from CB_control.models import AdminUser

aspect_ratio_list = ['1:1', '5:4', '3:2', '16:10', '16:9', '1.85:1', '2.35:1']

# Admin Log In Form
class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Login')

# Admin Registration Form
# This must be delete before it is used for actual production
# This is just temporary to allow the database to properly input an admin user
class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')

	def validate_username(self, username):
		user = AdminUser.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('That username is taken. Please choose a different one.')

	def validate_email(self, email):
		user = AdminUser.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('That email is taken. Please choose a different one.')


# Account
class UpdateAccountForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	submit = SubmitField('Update')

	def validate_username(self, username):
		if username.data != current_user.username:
			user = AdminUser.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('That username is taken. Please choose a different one.')

	def validate_email(self, email):
		if email.data != current_user.email:
			user = AdminUser.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('That email is taken. Please choose a different one.')

# Settings for device
class SettingsForm(FlaskForm):
	toggle_pay = BooleanField('Toggle Pay')
	price = IntegerField('Price per session in cents (ex. $3.50 = 350c)', validators=[InputRequired(), NumberRange(min=0, message="Cannot be negative")])
	charge_time_min = IntegerField('Allowed Charge Time (minutes)', validators=[InputRequired(), NumberRange(min=0, message="Cannot be negative")])
	charge_time_sec = IntegerField('Allowed Charge Time (seconds)', validators=[InputRequired(), NumberRange(min=0, message="Cannot be negative")])
	time_zone = SelectField('Timezone', choices=pytz.all_timezones)
	location = StringField('Location', validators=[Length(max=100, message="Max character is 100")])
	aspect_ratio = SelectField('Aspect Ratio', choices=aspect_ratio_list)

	submit = SubmitField('Update Settings')

# Slide Show Pictures
class SlideShowPicsForm(FlaskForm):
	picture = MultipleFileField('Upload Pictures', validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'jfif', 'pjpeg', 'pjp', 'png'])])
	submit = SubmitField('Upload Picture')