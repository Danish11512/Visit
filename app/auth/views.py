from . import auth
from flask import Flask, render_template, redirect, url_for, flash
from .forms import LoginForm, ChangePasswordForm
from flask_login import login_required
from werkzeug.security import check_password_hash
from .modules  import check_password_requirements
@auth.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():               
        return redirect(url_for('auth.login'))

    return render_template('auth/login.html', form=form)

@auth.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """
    View function for changing a user password.

    :return: Change Password page.
    """
    current_app.logger.info("Start function change_password() [VIEW]")
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if (
            check_password_hash(
                pwhash=current_user.password_list.p1, password=form.password.data
            )
            or check_password_hash(
                pwhash=current_user.password_list.p2, password=form.password.data
            )
            or check_password_hash(
                pwhash=current_user.password_list.p3, password=form.password.data
            )
            or check_password_hash(
                pwhash=current_user.password_list.p4, password=form.password.data
            )
            or check_password_hash(
                pwhash=current_user.password_list.p5, password=form.password.data
            )
        ):
            # If the inputted password is one of the user's last five passwords
            current_app.logger.info(
                "{} tried to change password. Failed: Used old password.".format(
                    current_user.email
                )
            )
            flash(
                "Your password cannot be the same as the last 5 passwords",
                category="error",
            )
            return render_template("auth/change_password.html", form=form)

        elif check_password_requirements(
            current_user.email,
            form.old_password.data,
            form.password.data,
            form.password2.data,
        ):
            # If password security requirements are met
            current_user.password_list.update(current_user.password_hash)
            current_user.password = form.password.data
            current_user.validated = True
            db.session.add(current_user)
            db.session.commit()
            current_app.logger.info(
                "{} changed their password.".format(current_user.email)
            )
            flash("Your password has been updated.", category="success")
            current_app.logger.info("End function logout() [VIEW]")
            return redirect(url_for("main.index"))

    current_app.logger.info("End function logout() [VIEW]")
    return render_template("auth/change_password.html", form=form)

# @app.route('/signup')
# def signup():
#     return render_template('signup.html')

# @app.route('/dashboard')
# def dashboard():
#     return render_template('dashboard.html')

if __name__ == '__auth__':
    app.run(debug=True)
