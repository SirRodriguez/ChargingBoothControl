from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from CB_control import db, login_manager
from flask_login import UserMixin


##################
#### Database ####
##################

@login_manager.user_loader
def load_user(user_id):
	return AdminUser.query.get(int(user_id))

class AdminUser(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)

	def __repr__(self):
		return f"Admin User('{self.username}', '{self.email}')"

	def get_reset_token(self, expires_sec=1800):
		s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
		return s.dumps({'user_id': self.id}).decode('utf-8')

	@staticmethod
	def verify_reset_token(token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return AdminUser.query.get(user_id)

###########
## Local ##
###########

class AdminKey():
	def __init__(self):
		self.admin_key = "None"

	def set_key(self, key):
		print("-----set key-----")
		print("-----key: ", self.key)
		self.admin_key = key
		print("-----admin key: ", self.admin_key)

	def get_key(self):
		print("-----get key-----")
		print("-----key: ", self.admin_key)
		return self.admin_key