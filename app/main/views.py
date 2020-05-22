from app import app
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import Form


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')