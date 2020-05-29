from flask import Flask
from flask_bootstrap import Bootstrap
app = Flask(__name__)


from .main import views

bootstrap = Bootstrap(app)
    

