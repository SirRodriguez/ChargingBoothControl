from flask import jsonify

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