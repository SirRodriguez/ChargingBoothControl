from flask import jsonify
from datetime import datetime, timedelta
from pytz import timezone
import pytz

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