from flask import render_template, Blueprint, url_for, redirect
from CB_control.main.forms import LoginForm

main = Blueprint('main', __name__)

@main.route("/", methods=['GET', 'POST'])
@main.route("/home", methods=['GET', 'POST'])
def home():

	form = LoginForm()
	if form.validate_on_submit():
		pass

	return render_template("home.html", title="Home", form=form)