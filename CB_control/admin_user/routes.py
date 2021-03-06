from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from CB_control import db, bcrypt, service_ip, admin_key
from CB_control.models import AdminUser
from CB_control.admin_user.forms import LoginForm, RegistrationForm, UpdateAccountForm, ResetPasswordForm
from CB_control.admin_user.utils import send_reset_email
import requests

admin_user = Blueprint('admin_user', __name__)

# Admin Login
@admin_user.route("/admin_login", methods=['GET', 'POST'])
def admin_login():
	form = LoginForm()
	if form.validate_on_submit():
		json_send = {}
		json_send["username"] = form.username.data
		json_send["password"] = form.password.data

		try:
			payload = requests.get(service_ip + '/site/admin_user/verify_user', json=json_send)
		except Exception as e:
			print(e)
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('error.server_error'))

		user = AdminUser.query.first()
		if payload.json()["user_verified"]:
			admin_key.set_key(payload.json()["admin_key"])
			login_user(user)
			next_page = request.args.get('next')
			return redirect(url_for('main.home'))
		else:
			flash('Loging Unsuccessful. Please check username and password', 'danger')

	return render_template("admin_user/login.html", title="Login", form=form)

# Log out
@admin_user.route("/logout")
def logout():
	# Logout from service
	try:
		payload = requests.get(service_ip + '/site/admin_user/logout')
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('error.server_error'))

	logout_user()
	return redirect(url_for('admin_user.admin_login'))

# Account Information
@admin_user.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	# Get account info from service
	try:
		payload = requests.get(service_ip + '/site/admin_user/account_info/' + admin_key.get_key())
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('error.server_error'))

	# Check admin Key is good
	if payload.status_code == 401:
		if current_user.is_authenticated:
			logout_user()
		flash('Please login to access this page.', 'info')
		return redirect(url_for('admin_user.admin_login'))

	form = UpdateAccountForm()
	if form.validate_on_submit():
		payload = {}

		# pack the updated account info
		payload["username"] = form.username.data
		payload["email"] = form.email.data

		# Send the updated account
		try:
			response = requests.put(service_ip + '/site/admin_user/update_account/' + admin_key.get_key(), json=payload)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('error.server_error'))

		# Check admin Key is good
		if response.status_code == 401:
			if current_user.is_authenticated:
				logout_user()
			flash('Please login to access this page.', 'info')
			return redirect(url_for('admin_user.admin_login'))

		# Check response
		if response.status_code == 204 or response.status_code == 200:
			flash('Account has been updated!', 'success')
		else:
			flash('Something happened and settings were not updated.', 'danger')

		return redirect(url_for('admin_user.account'))

	elif request.method == 'GET':
		form.username.data = payload.json()["username"]
		form.email.data = payload.json()["email"]

	return render_template("admin_user/account.html", title="Account Information", form=form, payload=payload)


@admin_user.route("/reset_password")
def reset_request():
	return redirect(service_ip + '/reset_password')




################################
# Old depreciated routes below #
################################

# Forgot password when logged out
@admin_user.route("/reset_password_OLD")
def reset_request_OLD():
	# !!!
	# These routes are depreciated because of non-working email
	return redirect(url_for('main.home'))

	if current_user.is_authenticated:
		return redirect(url_for('main.home'))

	return redirect(service_ip + '/reset_password')

#Change password when logged in
@admin_user.route("/change_password_OLD")
def change_request_OLD():
	# !!!
	# These routes are depreciated because of non-working email
	return redirect(url_for('main.home'))

	# Get account info from service
	try:
		payload = requests.get(service_ip + '/site/admin_user/account_info/' + admin_key.get_key())
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('error.server_error'))

	# Verify admin key
	if payload.status_code == 401:
		if current_user.is_authenticated:
			logout_user()
		flash('Please login to access this page.', 'info')
		return redirect(url_for('admin_user.admin_login'))

	user = AdminUser.query.first()
	send_reset_email(email=payload.json()["email"], user=user, logged_in=True)	

	flash('An email has been sent with instructions to reset your password.', 'info')
	return redirect(url_for('admin_user.account'))

@admin_user.route("/change_token_OLD/<token>", methods=['GET', 'POST'])
def change_token_OLD(token):
	# !!!
	# These routes are depreciated because of non-working email
	return redirect(url_for('main.home'))

	user = AdminUser.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired token', 'warning')
		return redirect(url_for('admin_user.admin_login'))

	form = ResetPasswordForm()
	if form.validate_on_submit():
		payload = {}
		payload["hashed_password"] = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

		try:
			response = requests.put(service_ip + '/site/admin_user/update_password/' + admin_key.get_key(), json=payload)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('error.server_error'))

		# Verify admin key
		if response.status_code == 401:
			if current_user.is_authenticated:
				logout_user()
			flash('Please login to access this page.', 'info')
			return redirect(url_for('admin_user.admin_login'))

		flash('Your password has been updated!', 'success')
		return redirect(url_for('admin_user.admin_login'))
	return render_template('admin_user/reset_token.html', title='Reset Password', form=form)