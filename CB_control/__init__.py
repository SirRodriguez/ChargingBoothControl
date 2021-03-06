from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from CB_control.config import Config
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'admin_user.admin_login'
login_manager.login_message_category = 'info'
mail = Mail()
service_ip = os.environ.get('SERVICE_IP')

from CB_control.models import AdminKey
admin_key = AdminKey()


def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(Config)

	db.init_app(app)
	bcrypt.init_app(app)
	login_manager.init_app(app)
	mail.init_app(app)


	from CB_control.main.routes import main
	from CB_control.error.routes import error
	from CB_control.admin_user.routes import admin_user
	from CB_control.slide_show.routes import slide_show
	from CB_control.settings.routes import settings
	from CB_control.data.routes import data
	from CB_control.device.routes import device

	app.register_blueprint(main)
	app.register_blueprint(error)
	app.register_blueprint(admin_user)
	app.register_blueprint(slide_show)
	app.register_blueprint(settings)
	app.register_blueprint(data)
	app.register_blueprint(device)

	return app