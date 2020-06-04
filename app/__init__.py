import os
import time
from flask import Flask, session
import logging
from flask_bootstrap import Bootstrap 
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

app = Flask(__name__)

from .main import views


bootstrap = Bootstrap(app)
app.config.from_object(Config)
migrate = Migrate(app)
db = SQLAlchemy(app)

from .main import main as main_blueprint

app.register_blueprint(main_blueprint)

from .auth import auth as auth_blueprint

app.register_blueprint(auth_blueprint, url_prefix="/auth")


