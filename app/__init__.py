import os
import time
from flask import Flask, session
import logging
from flask_bootstrap import Bootstrap
from logging import Formatter
from logging.handlers import RotatingFileHandler
from flask_kvsession import KVSessionExtension
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config
from simplekv.db.sql import SQLAlchemyStore

app = Flask(__name__)

from .main import views


bootstrap = Bootstrap(app)
app.config.from_object(Config)
migrate = Migrate()
db = SQLAlchemy()



# def create_app(config_name):  # App Factory
#     app = Flask(__name__)
#     app.config.from_object(config[config_name])

#     if os.environ.get("DATABASE_URL") is None:
#         app.config["SQLALCHEMY_DATABASE_URI"] = app.config.get(
#             "SQLALCHEMY_DATABASE_URI"
#         )
#     else:
#         app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    
#     config[config_name].init_app(app)
#     bootstrap.init_app(app)
#     migrate.init_app(app, db)
#     db.init_app(app)
#     with app.app_context():
#         # load_db(db)
#         store = SQLAlchemyStore(db.engine, db.metadata, "sessions")
#         kvsession = KVSessionExtension(store, app)
#         logfile_name = (
#             "logfile_directory" + "Visit" + time.strftime("%Y%m%d-%H%M%S") + ".log"
#         )
#         handler = RotatingFileHandler("LogFile", maxBytes=10000, backupCount=1)
#         handler.setFormatter(
#             Formatter(
#                 "%(asctime)s %(levelname)s: %(message)s " "[in %(pathname)s:%(lineno)d]"
#             )
#         )
#         handler.setLevel(logging.INFO)
#         app.logger.addHandler(handler)

#     @app.before_request
#     def func():
#         session.modified = True

#     return app
    

