from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import login_required
from CB_control import  service_ip
import requests

device = Blueprint('device', __name__)

# Show device settings options
@device.route("/device/<int:id>")
@login_required
def main(id):
	# Grab device location
	try:
		payload = requests.get(service_ip + '/site/location/' + str(id))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('error.server_error'))

	location = payload.json()["location"]


	return render_template("device/device.html", title="Device", id=id, location=location)


# Remove a device from the service
@device.route("/device/remove/<int:id>")
@login_required
def remove_device(id):
	# remove the device
	try:
		response = requests.delete(service_ip + '/site/remove_device/' + str(id))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('error.server_error'))

	if response.status_code == 204:
		flash('Device has been successfuly removed!', 'success')
	elif response.status_code == 400:
		flash('Device was not found in the server!', 'danger')
	else:
		flash("Oops! Something happened and the device was not deleted.", "danger")

	return redirect(url_for('main.home'))