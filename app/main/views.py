from . import main
from flask import Flask, render_template, redirect, url_for, flash,request
from .forms import CheckinForm
from flask_login import login_required
from ..decorators import admin_required
from sqlalchemy.orm import sessionmaker
from .. import db
from app.utils import eval_request_bool
from ..models import User

@main.route('/')
@main.route('/index', methods=["GET", "POST"])
def index():
    form = CheckinForm()

    if form.validate_on_submit():
        return render_template('main/checkin.html', fname=form.first_name.data, lname=form.last_name.data)

    return render_template('main/index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)