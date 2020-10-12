from flask import render_template, Blueprint, url_for, redirect, flash, request, json, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from CB_control import bcrypt, db, service_ip
from CB_control.models import AdminUser

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import requests
import secrets

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

# # Show device settings options
# @main.route("/device/<int:id>")
# @login_required
# def device(id):
# 	# Grab device location
# 	try:
# 		payload = requests.get(service_ip + '/site/location/' + str(id))
# 	except:
# 		flash("Unable to Connect to Server!", "danger")
# 		return redirect(url_for('error.server_error'))

# 	location = payload.json()["location"]


# 	return render_template("device/device.html", title="Device", id=id, location=location)


# # Remove a device from the service
# @main.route("/device/remove/<int:id>")
# @login_required
# def remove_device(id):
# 	# remove the device
# 	try:
# 		response = requests.delete(service_ip + '/site/remove_device/' + str(id))
# 	except:
# 		flash("Unable to Connect to Server!", "danger")
# 		return redirect(url_for('error.server_error'))

# 	if response.status_code == 204:
# 		flash('Device has been successfuly removed!', 'success')
# 	elif response.status_code == 400:
# 		flash('Device was not found in the server!', 'danger')
# 	else:
# 		flash("Oops! Something happened and the device was not deleted.", "danger")

# 	return redirect(url_for('main.home'))