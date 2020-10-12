from flask import Blueprint, render_template

error = Blueprint('error', __name__)

# Server error redirected page
@error.route("/error")
def server_error():
	return render_template("error/server.html", title="Error")