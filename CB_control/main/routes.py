from flask import render_template, Blueprint, url_for, redirect, flash
from flask_login import login_required
from CB_control import service_ip
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
		payload = requests.get(service_ip + '/site/get_all')
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('error.server_error'))


	device_id_list = payload.json()["device_id"]
	location_list = payload.json()["location"]

	devices = zip(location_list, device_id_list)

	return render_template("home.html", title="Home", devices=devices)