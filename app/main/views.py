from . import main
from flask import Flask, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from .forms import CheckinForm

@main.route('/')
@main.route('/index', methods=["GET", "POST"])
def index():
    if current_user.is_authenticated and (not current_user.validated):
        current_app.logger.info(
            "{} visited index but is not validated. Redirecting to /auth/change_password".format(
                current_user.email
            )
        )
        current_app.logger.info("End function index")
        return redirect(url_for("auth.change_password"))

    form = CheckinForm()

    if form.validate_on_submit():
        return render_template('main/checkin.html', fname=form.first_name.data, lname=form.last_name.data)

    return render_template('main/index.html', form=form)

    

if __name__ == '__main__':
    app.run(debug=True)