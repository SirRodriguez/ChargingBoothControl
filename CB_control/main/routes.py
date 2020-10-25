from flask import render_template, Blueprint, url_for, redirect, flash
from flask_login import login_required, current_user, logout_user
from CB_control import service_ip, admin_key
import requests

main = Blueprint('main', __name__)

# Home
@main.route("/")
def defualt():
	return redirect(url_for('admin_user.admin_login'))

# Home
@main.route("/home", methods=['GET', 'POST'])
@login_required
def home():
	try:
		payload = requests.get(service_ip + '/site/get_all/' + admin_key.get_key())
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('error.server_error'))

	# Check admin Key is good
	if payload.status_code == 401:
		if current_user.is_authenticated:
			logout_user()
		flash('Please login to access this page.', 'info')
		return redirect(url_for('admin_user.admin_login'))

	device_id_list = payload.json()["device_id"]
	location_list = payload.json()["location"]

	devices = zip(location_list, device_id_list)

	return render_template("home.html", title="Home", devices=devices)