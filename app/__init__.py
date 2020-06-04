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


