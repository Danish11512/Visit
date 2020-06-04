from . import main
from flask import Flask, render_template, redirect, url_for, flash
from .forms import CheckinForm


@main.route('/')
@main.route('/index', methods=["GET", "POST"])
def index():
    form = CheckinForm()

    if form.validate_on_submit():
        return render_template('main/checkin.html', fname=form.first_name.data, lname=form.last_name.data)

    return render_template('main/index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)