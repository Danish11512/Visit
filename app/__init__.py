import os
import time
from flask import Flask, session
from flask_login import LoginManager
from flask_bootstrap import Bootstrap 
from flask_moment import Moment
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from datetime import timedelta

app = Flask(__name__)

moment = Moment()
bootstrap = Bootstrap(app)
app.config.from_object(Config)
migrate = Migrate(app)
db = SQLAlchemy(app)
moment.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.refresh_view = 'relogin'
login_manager.needs_refresh_message = (u"Session timedout, please re-login")
app.permanent_session_lifetime = timedelta(minutes=35)

from .main import main as main_blueprint

app.register_blueprint(main_blueprint)

from .auth import auth as auth_blueprint

app.register_blueprint(auth_blueprint, url_prefix="/auth")




