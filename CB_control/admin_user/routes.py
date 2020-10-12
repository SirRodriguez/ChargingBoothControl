from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from CB_control import db, bcrypt
from CB_control.models import AdminUser
from CB_control.admin_user.forms import LoginForm, RegistrationForm, UpdateAccountForm

admin_user = Blueprint('admin_user', __name__)

# Admin Login
@admin_user.route("/admin_login", methods=['GET', 'POST'])
def admin_login():
	form = LoginForm()
	if form.validate_on_submit():
		user = AdminUser.query.filter_by(username=form.username.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user)
			next_page = request.args.get('next')
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
	form = UpdateAccountForm()
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('admin_user.account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email

	return render_template("admin_user/account.html", title="Account Information", form=form)