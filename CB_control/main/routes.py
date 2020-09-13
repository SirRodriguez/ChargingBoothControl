from flask import render_template, Blueprint, url_for, redirect, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from CB_control import bcrypt, db
from CB_control.models import AdminUser
from CB_control.main.forms import LoginForm, RegistrationForm

main = Blueprint('main', __name__)

# Admin Login
@main.route("/admin_login", methods=['GET', 'POST'])
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

	return render_template("login.html", title="Login", form=form)

# Register
# This will be removed in actuall production. This is just to get admin user in the database
@main.route("/register", methods=['GET', 'POST'])
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
    return render_template('register.html', title='Register', form=form)

# Log out
@main.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('main.admin_login'))

# Home
@main.route("/", methods=['GET', 'POST'])
@main.route("/home", methods=['GET', 'POST'])
@login_required
def home():

	return render_template("home.html", title="Home")


# Slide Show Pictures
@main.route("/slide_show_pics")
@login_required
def slide_show_pics():

	return render_template("slide_show_pics.html", title="Slide Show Pictures")

# Slide Show Pictures: Upload
@main.route("/slide_show_pics/upload")
@login_required
def upload():
	return render_template("upload.html", title="Picture Upload")


# Slide Show Pictures: Remove
@main.route("/slide_show_pics/remove")
@login_required
def remove():
	return render_template("remove.html", title="Picture Removal")