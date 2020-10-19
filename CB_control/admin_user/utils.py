from flask import url_for
from CB_control import mail
from flask_mail import Message

def send_reset_email(email, user, logged_in=False):
	token = user.get_reset_token()
	msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[email])
	if logged_in:
		msg.body = f'''To reset your password, visit the following link:

{url_for('admin_user.change_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no change will be made.
'''
	else:
		msg.body = f'''To reset your password, visit the following link:

{url_for('admin_user.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no change will be made.
'''
	mail.send(msg)