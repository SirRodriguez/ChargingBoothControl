from flask import jsonify, current_app
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import os
from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
import secrets

def get_min_sec(seconds):
	minutes = seconds // 60
	sec = seconds - (minutes * 60)
	return minutes, sec

def removals_json(removals):
	print(type(removals))
	print(removals)

	rem_list = removals.split(",")
	print(type(rem_list))
	print(rem_list)

	# fix index
	for index, value in enumerate(rem_list):
		rem_list[index] = int(rem_list[index])-1

	print(rem_list)

	payload = {}
	payload["removlas"] = rem_list

	resp = jsonify(payload)
	# resp.status_code = 200
	return resp

def get_offset_dates_initiated(sessions, time_offset):
	fmt = '%b %d, %Y - %I:%M:%S %p'
	dates = []

	zone = timezone(time_offset)
	for session in sessions:
		# utc_time = pytz.utc.localize(session.date_initiated)
		date_initiated=datetime(
			year=session["date_initiated_year"],
			month=session["date_initiated_month"],
			day=session["date_initiated_day"], 
			hour=session["date_initiated_hour"], 
			minute=session["date_initiated_minute"],
			second=session["date_initiated_second"]
			)

		utc_time = pytz.utc.localize(date_initiated)
		local_time = utc_time.astimezone(zone)

		dates.append(local_time.strftime(fmt))

	return dates

def remove_png():
	files_path = os.path.join(current_app.root_path, 'static', 'data_files')
	files = [f for f in listdir(files_path) if isfile(join(files_path, f))]
	for file in files:
		f_name, f_ext = os.path.splitext(file)
		if f_ext == ".png":
			full_path = os.path.join(current_app.root_path, 'static', 'data_files', file)
			os.remove(full_path)

def count_years(dates):
	years = {}

	for date in dates:
		yr = date.split(" ")[2]
		years[yr] = years.get(yr, 0) + 1


	return years

def create_bar_years(years):
	yrs = list(years.keys())
	vls = list(years.values())

	fig = plt.figure(figsize = (10, 5))

	# Create the bar plot
	plt.bar(yrs, vls)

	# Set the labels
	plt.title("Number of Sessions for each year", fontsize=20)
	plt.ylabel("Number of Sessions", fontsize=15)
	plt.xlabel("Year", fontsize=15)

def save_figure():
	fig_name = secrets.token_hex(8) + ".png"
	pic_path = os.path.join(current_app.root_path, 'static', 'data_files', fig_name)
	plt.savefig(pic_path)

	return fig_name

def count_months(dates, year):
	# initialize the months
	months = {
		'Jan' : 0,
		'Feb' : 0,
		'Mar' : 0,
		'Apr' : 0,
		'May' : 0,
		'Jun' : 0,
		'Jul' : 0,
		'Aug' : 0,
		'Sep' : 0,
		'Oct' : 0,
		'Nov' : 0,
		'Dec' : 0
	}

	# Grab the sessions in each month
	for date in dates:
		date_list = date.split(" ")
		yr = date_list[2]

		if yr == year:
			mth = date_list[0]
			months[mth] += 1

	return months

def create_bar_months(months, year):
	mth = list(months.keys())
	vls = list(months.values())

	fig = plt.figure(figsize = (10, 5))

	# Create the bar plot
	plt.bar(mth, vls)

	# Set the labels
	plt.title("Number of Sessions for " + year, fontsize=20)
	plt.ylabel("Number of Sessions", fontsize=15)
	plt.xlabel("Month", fontsize=15)

def count_days(dates, year, month):
	# This is to get how many days each month has
	days_of_months = {
		'Jan' : 31,
		'Feb' : 29, # Because of leap year, it has 29
		'Mar' : 31,
		'Apr' : 30,
		'May' : 31,
		'Jun' : 30,
		'Jul' : 31,
		'Aug' : 31,
		'Sep' : 30,
		'Oct' : 31,
		'Nov' : 30,
		'Dec' : 31
	}

	# initialize days
	days = {}
	for d in range(days_of_months[month]):
		days[d+1] = 0

	# Grab the sessions for the month
	for date in dates:
		date_list = date.split(" ")
		yr = date_list[2]
		mth = date_list[0]

		if yr == year and mth == month:
			dy = int(date_list[1][:-1])
			days[dy] += 1


	return days

def create_bar_days(days, month, year):
	dys = list(days.keys())
	vls = list(days.values())

	fig = plt.figure(figsize = (10, 5))

	# Create the bar plot
	plt.bar(dys, vls)

	# Make sure all x ticks show
	plt.xticks(dys)

	# Set the labels
	plt.title("Number of Sessions for " + month + ", " + year, fontsize=20)
	plt.ylabel("Number of Sessions", fontsize=15)
	plt.xlabel("Day", fontsize=15)
