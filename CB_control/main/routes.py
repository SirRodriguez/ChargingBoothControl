from flask import render_template, Blueprint, url_for, redirect, flash, request, json, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from CB_control import bcrypt, db, service_ip
from CB_control.models import AdminUser
from CB_control.main.forms import (LoginForm, RegistrationForm, UpdateAccountForm, SettingsForm,
									SlideShowPicsForm, RemovePictureForm, YearForm)
from CB_control.main.utils import (get_min_sec, removals_json, get_offset_dates_initiated, remove_png, 
									count_years, create_bar_years, save_figure, count_months,
									create_bar_months)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import requests

main = Blueprint('main', __name__)

# Home
@main.route("/")
def defualt():
	return redirect(url_for('main.admin_login'))

# Server error redirected page
@main.route("/error")
def error():
	# logout_user()
	return render_template("error.html", title="Error")

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
@main.route("/home", methods=['GET', 'POST'])
@login_required
def home():
	try:
		payload = requests.get(service_ip + '/site/get_all')		
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('main.error'))


	device_id_list = payload.json()["device_id"]
	location_list = payload.json()["location"]

	devices = zip(location_list, device_id_list)

	return render_template("home.html", title="Home", devices=devices)

# Show device settings options
@main.route("/device/<int:id>")
@login_required
def device(id):
	# Grab device location
	try:
		payload = requests.get(service_ip + '/site/location/' + str(id))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('main.error'))

	location = payload.json()["location"]


	return render_template("device.html", title="Device", id=id, location=location)


# Slide Show Pictures
@main.route("/slide_show_pics/<int:id>")
@login_required
def slide_show_pics(id):
	# Grab device location
	try:
		payload = requests.get(service_ip + '/site/location/' + str(id))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('main.error'))

	location = payload.json()["location"]

	return render_template("slide_show_pics.html", title="Slide Show Pictures", location=location, id=id)

# Slide Show Pictures: Upload
@main.route("/slide_show_pics/upload/<int:id>", methods=['GET', 'POST'])
@login_required
def upload(id):
	# Grab device location and image number
	try:
		# payload = requests.get(service_ip + '/site/location/' + str(id))
		payload = requests.get(service_ip + '/site/location_image_count/' + str(id))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('main.error'))

	payload_json = payload.json()
	location = payload_json["location"]
	image_count = payload_json["image_count"]
	# print(image_count)

	form = SlideShowPicsForm()
	if form.validate_on_submit():
		image_files = []
		for file in form.picture.data:
			image_files.append(('image', ( file.filename, file.read() )  ))
			print(file.filename)

		# Do the post here
		response = requests.post(service_ip + '/site/images/upload/' + str(id), files=image_files)

		flash('Pictures has been uploaded', 'success')
		return redirect(url_for('main.upload', id=id))

	return render_template("upload.html", title="Picture Upload", location=location, form=form, service_ip=service_ip, id=id, image_count=image_count)


# Slide Show Pictures: Remove
@main.route("/slide_show_pics/remove/<int:id>", methods=['GET', 'POST'])
@login_required
def remove(id):
	# Grab device location and image count
	try:
		# payload = requests.get(service_ip + '/site/location/' + str(id))
		payload = requests.get(service_ip + '/site/location_image_count/' + str(id))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('main.error'))

	payload_json = payload.json()
	location = payload_json["location"]
	image_count = payload_json["image_count"]

	form = RemovePictureForm()
	if form.validate_on_submit():
		# Post a delete image files here

		# removals = removals_json(form.removals.data)

		try:
			print("in try")
			response = requests.delete(service_ip + '/site/remove_images/' + str(id) + '/' + form.removals.data)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('main.error'))

		if response.status_code == 204:
			flash('Images have been successfuly removed! Refresh your browser if there is no change.', 'success')
		elif response.status_code == 400:
			flash('Image was not found in the server!', 'danger')
		else:
			flash("Oops! Something happened and the images were not deleted.", "danger")
		

	return render_template("remove.html", title="Picture Removal", location=location, form=form, service_ip=service_ip, id=id, image_count=image_count)

# Settings for the device
@main.route("/device/settings/<int:id>", methods=['GET', 'POST'])
@login_required
def device_settings(id):

	form = SettingsForm()
	if form.validate_on_submit():
		payload = {}

		payload["toggle_pay"] = form.toggle_pay.data
		payload["price"] = form.price.data
		# Settings.query.first().charge_time = form.charge_time.data
		minutes = form.charge_time_min.data
		seconds = form.charge_time_sec.data
		payload["charge_time"] = minutes*60 + seconds;
		payload["time_offset"] = form.time_zone.data
		payload["location"] = form.location.data

		# Check if aspect ration is different so that it can resize all images
		# resize = False
		# if Settings.query.first().aspect_ratio_width != float(form.aspect_ratio.data.split(":")[0]) and \
		# 	Settings.query.first().aspect_ratio_height != float(form.aspect_ratio.data.split(":")[1]):
		# 	resize = True

		payload["aspect_ratio_width"] = float(form.aspect_ratio.data.split(":")[0])
		payload["aspect_ratio_height"] = float(form.aspect_ratio.data.split(":")[1])

		# if resize:
		# 	pic_files = PFI()
		# 	pic_files.resize_all(Settings.query.first().aspect_ratio_width, Settings.query.first().aspect_ratio_height)

		# db.session.commit()
		
		try:
			response = requests.put(service_ip + '/site/settings/update/' + str(id), json=payload)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('main.error'))

		if response.status_code == 204 or response.status_code == 200:
			flash('Settings have been updated!', 'success')
		elif response.status_code == 400:
			flash('Server could not find device!', 'danger')
		else:
			flash('Something happened and settings were not updated.', 'danger')

		return redirect(url_for('main.device_settings', id=id))
	elif request.method == 'GET':
		# Grab device settings
		try:
			payload = requests.get(service_ip + '/site/settings/' + str(id))
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('main.error'))

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

	return render_template("settings.html", title="Settings", form=form)


# Device data
@main.route("/device/data/<int:id>")
@login_required
def data(id):
	# Grab device location
	try:
		payload = requests.get(service_ip + '/site/location/' + str(id))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('main.error'))

	location = payload.json()["location"]

	return render_template("data.html", title="Data", location=location, id=id)



# List Data
@main.route("/device/list_data/<int:id>")
@login_required
def list_data(id):
	# Grab device location
	try:
		payload = requests.get(service_ip + '/site/location/' + str(id))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('main.error'))

	location = payload.json()["location"]

	# Grab the device data listed 

	# Pagination page
	page = request.args.get('page', 1, type=int)

	try:
		payload = requests.get(service_ip + '/site/sessions/' + str(id) + '/' + str(page))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('register.error'))

	# Later combine the two requests to speed up
	try:
		payload_sett = requests.get(service_ip + '/site/settings/' + str(id))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('register.error'))

	pl_json = payload.json()
	sess_list = pl_json["sessions"]
	iter_pages = pl_json["iter_pages"]

	# Get the settings
	settings = payload_sett.json()

	date_strings = get_offset_dates_initiated(sessions=sess_list,
									time_offset=settings["time_offset"])

	sessions_and_dates = zip(sess_list, date_strings) # Pack them together to iterate simultaniously
	return render_template("list_data.html", title="List Data", iter_pages=iter_pages, 
							page=page, sessions_and_dates=sessions_and_dates, id=id)


@main.route("/device/graph_data/<int:id>")
@login_required
def graph_data(id):
	# Grab device location
	try:
		payload = requests.get(service_ip + '/site/location/' + str(id))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('main.error'))

	location = payload.json()["location"]

	return render_template("graph_data.html", title="Graph Data", location=location, id=id)

@main.route("/device/graph_data/all_years/<int:id>")
@login_required
def graph_all_years(id):
	# Grab device location
	try:
		payload = requests.get(service_ip + '/site/location/' + str(id))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('main.error'))

	location = payload.json()["location"]

	# Grab the sessions
	try:
		payload = requests.get(service_ip + '/site/all_sessions/' + str(id))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('register.error'))

	# Get the sessions
	sess_list = payload.json()["sessions"]

	# Later combine the two requests to speed up
	try:
		payload_sett = requests.get(service_ip + '/site/settings/' + str(id))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('register.error'))

	# Get the settings
	settings = payload_sett.json()

	# Delete old pic files
	remove_png()

	# This is what will be used for the bar graph
	date_strings = get_offset_dates_initiated(sessions=sess_list,
									time_offset=settings["time_offset"])

	# For every year, count how many sessions occured
	# Returns a dictionary
	years = count_years(dates=date_strings)

	create_bar_years(years=years)

	# Create the pic file to show
	pic_name = save_figure()

	return render_template("graph_all_years.html", title="All Years", id=id, location=location, pic_name=pic_name)

@main.route("/device/graph_data/year/<int:id>", methods=['GET', 'POST'])
@login_required
def graph_year(id):
	# Grab device location
	try:
		payload = requests.get(service_ip + '/site/location/' + str(id))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('main.error'))

	location = payload.json()["location"]

	form = YearForm()
	if form.validate_on_submit():
		# Grab the sessions
		# sessions = Session.query.all()
		try:
			payload = requests.get(service_ip + '/site/all_sessions/' + str(id))
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('register.error'))

		# Later combine the two requests to speed up
		try:
			payload_sett = requests.get(service_ip + '/site/settings/' + str(id))
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('register.error'))

		
		# Get the sessions
		sess_list = payload.json()["sessions"]

		# Get the settings
		settings = payload_sett.json()


		# Delete old pic files
		remove_png()

		# This is what will be used for the bar graph
		date_strings = get_offset_dates_initiated(sessions=sess_list,
									time_offset=settings["time_offset"])

		# For every month in the given year, count how many sessions occured
		# returns a dictionary
		months = count_months(dates=date_strings, year=form.year.data)

		create_bar_months(months=months, year=form.year.data)

		# Create the pic file to show
		pic_name = save_figure()

		return render_template("graph_year.html", title="All Years", id=id, location=location, form=form, pic_name=pic_name)

	return render_template("graph_year.html", title="All Years", id=id, location=location, form=form)

@main.route("/device/graph_data/month/<int:id>", methods=['GET', 'POST'])
@login_required
def graph_month(id):
	# Grab device location
	try:
		payload = requests.get(service_ip + '/site/location/' + str(id))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('main.error'))

	location = payload.json()["location"]

	return render_template("graph_month.html", title="All Years", id=id, location=location)

@main.route("/device/graph_data/month/<int:id>", methods=['GET', 'POST'])
@login_required
def graph_day(id):
	# Grab device location
	try:
		payload = requests.get(service_ip + '/site/location/' + str(id))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('main.error'))

	location = payload.json()["location"]

	return render_template("graph_day.html", title="All Years", id=id, location=location)

# Remove a device from the service
@main.route("/device/remove/<int:id>")
@login_required
def remove_device(id):
	# remove the device
	try:
		response = requests.delete(service_ip + '/site/remove_device/' + str(id))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('main.error'))

	if response.status_code == 204:
		flash('Device has been successfuly removed!', 'success')
	elif response.status_code == 400:
		flash('Device was not found in the server!', 'danger')
	else:
		flash("Oops! Something happened and the device was not deleted.", "danger")

	return redirect(url_for('main.home'))


# Account Information
@main.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('main.account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email

	return render_template("account.html", title="Account Information", form=form)