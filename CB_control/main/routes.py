from flask import render_template, Blueprint, url_for, redirect

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
	return render_template("home.html")