from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import login_required
from CB_control import  service_ip
from CB_control.device.forms import LoginForm
import requests

device = Blueprint('device', __name__)

# Show device settings options
@device.route("/device/<int:id>/<string:location>")
@login_required
def main(id, location):
	return render_template("device/device.html", title="Device", id=id, location=location)


@device.route("/device/confirm_remove/<int:id>/<string:location>", methods=['GET', 'POST'])
@login_required
def confirm_removal(id, location):
	form = LoginForm()
	if form.validate_on_submit():
		# Contact the server
		try:
			payload = requests.get(service_ip + '/site/admin_user/verify_user/' + form.username.data + '/' + form.password.data)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('error.server_error'))

		if payload.json()["user_verified"]:
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

	return render_template("device/remove_confirm.html", title="Confirm Removal", form=form, location=location)

# Depretiated
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