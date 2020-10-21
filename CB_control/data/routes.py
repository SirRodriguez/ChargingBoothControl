from flask import Blueprint, flash, redirect, url_for, render_template, request
from flask_login import login_required
from CB_control import service_ip
from CB_control.data.utils import (get_offset_dates_initiated, remove_png, count_years, create_bar_years,
									save_figure, count_months, create_bar_months, count_days, 
									create_bar_days, count_hours, create_bar_hours)
from CB_control.data.forms import YearForm, MonthForm, DayForm
import requests

data = Blueprint('data', __name__)

# Device data
@data.route("/device/data/<int:id>/<string:location>")
@login_required
def main(id, location):
	return render_template("data/data.html", title="Data", location=location, id=id)

# List Data
@data.route("/device/list_data/<int:id>/<string:location>")
@login_required
def list_data(id, location):
	# Grab the device data listed 

	# Pagination page
	page = request.args.get('page', 1, type=int)

	try:
		payload = requests.get(service_ip + '/site/sessions/' + str(id) + '/' + str(page))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('error.server_error'))

	pl_json = payload.json()
	sess_list = pl_json["sessions"]
	iter_pages = pl_json["iter_pages"]
	settings = pl_json["settings"]

	date_strings = get_offset_dates_initiated(sessions=sess_list,
									time_offset=settings["time_offset"])

	sessions_and_dates = zip(sess_list, date_strings) # Pack them together to iterate simultaniously
	return render_template("data/list_data.html", title="List Data", iter_pages=iter_pages, 
							page=page, sessions_and_dates=sessions_and_dates, id=id)

@data.route("/device/graph_data/<int:id>/<string:location>")
@login_required
def graph_data(id, location):
	return render_template("data/graph_data.html", title="Graph Data", location=location, id=id)

@data.route("/device/graph_data/all_years/<int:id>/<string:location>")
@login_required
def graph_all_years(id, location):
	# Grab the sessions
	try:
		payload = requests.get(service_ip + '/site/all_sessions/' + str(id))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('error.server_error'))

	# Get the sessions and settings
	pl_json = payload.json()
	sess_list = pl_json["sessions"]
	settings = pl_json["settings"]

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

	return render_template("data/graph_all_years.html", title="All Years", id=id, location=location, pic_name=pic_name)

@data.route("/device/graph_data/year/<int:id>/<string:location>", methods=['GET', 'POST'])
@login_required
def graph_year(id, location):
	form = YearForm()
	if form.validate_on_submit():
		# Grab the sessions
		try:
			payload = requests.get(service_ip + '/site/all_sessions/' + str(id))
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('error.server_error'))

		pl_json = payload.json()
		sess_list = pl_json["sessions"]
		settings = pl_json["settings"]

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

		return render_template("data/graph_year.html", title="All Years", id=id, location=location, form=form, pic_name=pic_name)

	return render_template("data/graph_year.html", title="All Years", id=id, location=location, form=form)

@data.route("/device/graph_data/month/<int:id>/<string:location>", methods=['GET', 'POST'])
@login_required
def graph_month(id, location):
	form = MonthForm()
	if form.validate_on_submit():
		# Grab the sessions
		try:
			payload = requests.get(service_ip + '/site/all_sessions/' + str(id))
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('error.server_error'))

		pl_json = payload.json()
		sess_list = pl_json["sessions"]
		settings = pl_json["settings"]

		# Delete old pic files
		remove_png()

		# This is what will be used for the bar graph
		date_strings = get_offset_dates_initiated(sessions=sess_list,
									time_offset=settings["time_offset"])

		# For every day in a given month of a given year, count how many sessions occured
		# Returns a dictionary
		days = count_days(dates=date_strings, year=form.year.data, month=form.month.data)

		create_bar_days(days=days, month=form.month.data, year=form.year.data)

		# Create the pic file to show
		pic_name = save_figure()

		return render_template("data/graph_month.html", title="All Years", id=id, location=location, form=form, pic_name=pic_name)

	return render_template("data/graph_month.html", title="All Years", id=id, location=location, form=form)

@data.route("/device/graph_data/day/<int:id>/<string:location>", methods=['GET', 'POST'])
@login_required
def graph_day(id, location):
	form = DayForm()
	if form.validate_on_submit():
		# Grab the sessions
		try:
			payload = requests.get(service_ip + '/site/all_sessions/' + str(id))
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('error.server_error'))
		
		pl_json = payload.json()
		sess_list = pl_json["sessions"]
		settings = pl_json["settings"]

		# Delete old pic files
		remove_png()

		# This is what will be used for the bar graph
		date_strings = get_offset_dates_initiated(sessions=sess_list,
									time_offset=settings["time_offset"])


		# fix form.day.data (ex from 4 to 04)
		if int(form.day.data) < 10:
			form.day.data = '0' + str(int(form.day.data))

		# For every hour in a given day of a given month of a given year, count the sessions
		# Returns a dictionary
		hours = count_hours(dates=date_strings, day=form.day.data, month=form.month.data, year=form.year.data)

		create_bar_hours(hours=hours, day=form.day.data, month=form.month.data, year=form.year.data)

		# Create the pic file to show
		pic_name = save_figure()

		
		return render_template("data/graph_day.html", title="All Years", id=id, location=location, form=form, pic_name=pic_name)		


	return render_template("data/graph_day.html", title="All Years", id=id, location=location, form=form)