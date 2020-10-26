from flask import Blueprint, request, flash, redirect, url_for, render_template
from flask_login import login_required
from CB_control import service_ip, admin_key
from CB_control.settings.forms import SettingsForm
from CB_control.settings.utils import get_min_sec
import requests

settings = Blueprint('settings', __name__)

# Settings for the device
@settings.route("/device/settings/<int:id>", methods=['GET', 'POST'])
@login_required
def device_settings(id):

	form = SettingsForm()
	if form.validate_on_submit():
		payload = {}

		payload["toggle_pay"] = form.toggle_pay.data
		payload["price"] = form.price.data

		minutes = form.charge_time_min.data
		seconds = form.charge_time_sec.data
		payload["charge_time"] = minutes*60 + seconds;

		payload["time_offset"] = form.time_zone.data
		payload["location"] = form.location.data

		payload["aspect_ratio_width"] = float(form.aspect_ratio.data.split(":")[0])
		payload["aspect_ratio_height"] = float(form.aspect_ratio.data.split(":")[1])
		
		try:
			response = requests.put(service_ip + '/site/settings/update/' + str(id) + '/' + admin_key.get_key(), json=payload)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('error.server_error'))

		# Check admin Key is good
		if response.status_code == 401:
			if current_user.is_authenticated:
				logout_user()
			flash('Please login to access this page.', 'info')
			return redirect(url_for('admin_user.admin_login'))

		if response.status_code == 204 or response.status_code == 200:
			flash('Settings have been updated!', 'success')
		elif response.status_code == 400:
			flash('Server could not find device!', 'danger')
		else:
			flash('Something happened and settings were not updated.', 'danger')

		return redirect(url_for('settings.device_settings', id=id))
	elif request.method == 'GET':
		# Grab device settings
		try:
			payload = requests.get(service_ip + '/site/settings/' + str(id) + '/' + admin_key.get_key())
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('error.server_error'))

		# Check admin Key is good
		if payload.status_code == 401:
			if current_user.is_authenticated:
				logout_user()
			flash('Please login to access this page.', 'info')
			return redirect(url_for('admin_user.admin_login'))

		settings = payload.json()
		
		form.toggle_pay.data = settings["toggle_pay"]
		form.price.data = settings["price"]
		minutes, seconds = get_min_sec(seconds=settings["charge_time"])
		form.charge_time_min.data = minutes
		form.charge_time_sec.data = seconds
		form.time_zone.data = settings["time_offset"]
		form.location.data = settings["location"]
		form.aspect_ratio.data = str( int(settings["aspect_ratio_width"]) if (settings["aspect_ratio_width"]).is_integer() else settings["aspect_ratio_width"] ) \
									+ ":" + str( int(settings["aspect_ratio_height"]) if (settings["aspect_ratio_height"]).is_integer() else settings["aspect_ratio_height"] ) 

	return render_template("settings/settings.html", title="Settings", form=form)
