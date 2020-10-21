from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import login_required
from CB_control import service_ip
from CB_control.slide_show.forms import SlideShowPicsForm, RemovePictureForm
import requests
import secrets

slide_show = Blueprint('slide_show', __name__)

# Slide Show Pictures
@slide_show.route("/slide_show_pics/<int:id>/<string:location>")
@login_required
def slide_show_pics(id, location):
	return render_template("slide_show/slide_show_pics.html", title="Slide Show Pictures", location=location, id=id)

# Slide Show Pictures: Upload
@slide_show.route("/slide_show_pics/upload/<int:id>/<string:location>", methods=['GET', 'POST'])
@login_required
def upload(id, location):
	# Grab device image count
	try:
		payload = requests.get(service_ip + '/site/image_count/' + str(id))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('error.server_error'))

	image_count = payload.json()["image_count"]

	form = SlideShowPicsForm()
	if form.validate_on_submit():
		image_files = []
		for file in form.picture.data:
			image_files.append(('image', ( file.filename, file.read() )  ))

		# Do the post here
		response = requests.post(service_ip + '/site/images/upload/' + str(id), files=image_files)

		flash('Pictures has been uploaded', 'success')
		return redirect(url_for('slide_show.upload', id=id, location=location))

	random_hex = secrets.token_hex(8)

	return render_template("slide_show/upload.html", 
							title="Picture Upload", 
							location=location, 
							form=form, 
							service_ip=service_ip, 
							id=id, 
							image_count=image_count,
							random_hex=random_hex)


# Slide Show Pictures: Remove
@slide_show.route("/slide_show_pics/remove/<int:id>/<string:location>", methods=['GET', 'POST'])
@login_required
def remove(id, location):
	form = RemovePictureForm()
	if form.validate_on_submit():
		# Post a delete image files here
		try:
			response = requests.delete(service_ip + '/site/remove_images/' + str(id) + '/' + form.removals.data)
		except:
			flash("Unable to Connect to Server!", "danger")
			return redirect(url_for('error.server_error'))

		if response.status_code == 204:
			flash('Images have been successfuly removed!', 'success')
		elif response.status_code == 400:
			flash('Image was not found in the server!', 'danger')
		else:
			flash("Oops! Something happened and the images were not deleted.", "danger")
		

	# Grab device location and image count
	try:
		payload = requests.get(service_ip + '/site/image_count/' + str(id))
	except:
		flash("Unable to Connect to Server!", "danger")
		return redirect(url_for('error.server_error'))

	image_count = payload.json()["image_count"]

	random_hex = secrets.token_hex(8)

	return render_template("slide_show/remove.html", 
							title="Picture Removal", 
							location=location, 
							form=form, 
							service_ip=service_ip, 
							id=id, 
							image_count=image_count,
							random_hex=random_hex)