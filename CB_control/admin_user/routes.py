from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from CB_control import db, bcrypt, service_ip
from CB_control.models import AdminUser
from CB_control.admin_user.forms import LoginForm, RegistrationForm, UpdateAccountForm
import requests

admin_user = Blueprint('admin_user', __name__)

# Admin Login
@admin_user.route("/admin_login", methods=['GET', 'POST'])
def admin_login():
	form = LoginForm()
	if form.validate_on_submit():
		try:
			payload = requests.get(service_ip + '/site/admin_user/verify_user/' + form.username.data + '/' + form.password.data)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('error.server_error'))

		user = AdminUser.query.first()
		if payload.json()["user_verified"]:
			login_user(user)
			next_page = request.args.get('nest')
			return redirect(url_for('main.home'))
		else:
			flash('Loging Unsuccessful. Please check username and password', 'danger')

	return render_template("admin_user/login.html", title="Login", form=form)

# Register
# This will be removed in actuall production. This is just to get admin user in the database
@admin_user.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = AdminUser(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.home'))
    return render_template('admin_user/register.html', title='Register', form=form)

# Log out
@admin_user.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('admin_user.admin_login'))

# Account Information
@admin_user.route("/account", methods=['GET', 'POST'])
@login_required
def account():

	# Get account info from service
	try:
		payload = requests.get(service_ip + '/site/admin_user/account_info')
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('error.server_error'))


	form = UpdateAccountForm()
	if form.validate_on_submit():
		payload = {}

		# pack the updated account info
		payload["username"] = form.username.data
		payload["email"] = form.email.data

		# Send the updated account
		try:
			response = requests.put(service_ip + '/site/admin_user/update_account/', json=payload)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('error.server_error'))

		# Check response
		if response.status_code == 204 or response.status_code == 200:
			flash('Account has been updated!', 'success')
		else:
			flash('Something happened and settings were not updated.', 'danger')

		return redirect(url_for('admin_user.account'))

	elif request.method == 'GET':
		form.username.data = payload.json()["username"]
		form.email.data = payload.json()["email"]

	return render_template("admin_user/account.html", title="Account Information", form=form)