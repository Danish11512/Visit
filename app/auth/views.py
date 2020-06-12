from . import auth
from flask import Flask, render_template, redirect, url_for, flash, current_app
from ..models import User
from flask_login import login_required, login_user, logout_user, current_user
from .forms import LoginForm, ChangePasswordForm
from .modules import increase_login_attempt, reset_login_attempts, check_previous_passwords, check_password_requirements,update_user_password
from app import db

@auth.route('/login', methods=["GET", "POST"])
def login():

    if current_user.is_authenticated and current_user.validated:
        # if the user is is already authenticated and validated let them in 
        current_app.logger.info("User is already logged in, routing to auth/index")
        return redirect(url_for('auth.index'))

    form = LoginForm()
    if form.validate_on_submit():  
        user = User.query.filter_by(email= form.email.data).first()

        if user:
            if user.login_attempts < 3 : 
                # if user exists and their login attempts are less than 3 they can be logged in after chacking 
                if user.verify_password(form.password.data) and user.validated:
                    # If user password is valid and they are validated, log them in 
                    login_user(user, remember=True)
                    current_app.logger.info("User {} logged in and login attempts reset to 0, redirecting to auth/index".format(user.email))
                    reset_login_attempts(user)
                    return redirect(url_for("auth.index"))
                elif user.verify_password(form.password.data) and (not user.validated) :
                    # if user is not validated then you log them in but redirect them to reset password
                    login_user(user, remember=True)
                    current_app.logger.info("User {} logged in but not verified, login attempts reset to 0, redirecting to auth/change_password".format(user.email))
                    reset_login_attempts(user)
                    return redirect(url_for("auth.change_password"))
                else:
                    # If user is not valid increase login attempt and return unable to log in 
                    increase_login_attempt(user)
                    current_app.logger.info("User {} failed to log in, login attempts increased to {}".format(user.email, user.login_attempts))
                    flash("Invalid username or password", category="error")
                    return redirect(url_for("auth.login"))
            else:
                # They cannnot log in if the max attempt has been reached
                current_app.logger.info("User {} has reached max login attempts".format(user.email))
                flash("You have reached the maximum number of log in attempts, contact an adminsitrator for more details", category="error")
                return redirect(url_for("auth.login"))
        else:
            # if user is not in the database, return an error
            current_app.logger.info("User {} is not in the system".format(current_user))
            flash('Username or password are incorrect', category='error')
            return redirect(url_for("auth.login"))
    return render_template('auth/login.html', form=form)



@auth.route('/')
@auth.route('/index', methods=["GET", "POST"])
@login_required
def index():
    if current_user.is_authenticated and (not current_user.validated):
        # if the user is not valitaed they will be routed back to change password form 
        current_app.logger.info("{} visited index but is not validated. Redirecting to /auth/change_password".format(current_user.email))
        return redirect(url_for("auth.change_password"))
    else:   
        flash("Logged in successfully")
        return render_template("auth/index.html", name=current_user.first_name)


@auth.route('/logout')
@login_required
def logout():
    # Log out user
    logout_user()
    current_app.logger.info("User logged out")
    return redirect(url_for('auth.login'))


@auth.route('/change_password', methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    current_app.logger.info("Checking submitted password")
    if form.validate_on_submit():
        current_app.logger.info("Checking submitted password")

        if check_previous_passwords(current_user.id, form.password.data):
            # If the inputted password is one of the user's last five passwords , redirect back to form to put a new password
            current_app.logger.info("User {} tried to change password but used old password.".format(current_user.email))
            flash("Your password cannot be the same as the last 5 passwords",category="error")
            return render_template("auth/change_password.html", form=form)
        else:
            if check_password_requirements(current_user.email,form.old_password.data,form.password.data,form.password2.data):
                # If password security requirements are met, update the user's password and validate them
                update_user_password(current_user.id, form.password.data)

                if (not current_user.validated):
                    current_user.validated = True
                    db.session.commit()
                current_app.logger.info("User {} changed their password.".format(current_user.email))
                flash("Your password has been updated.", category="success")
                return redirect(url_for("auth.index"))

    return render_template("auth/change_password.html", form=form)


if __name__ == '__auth__':
    app.run(debug=True)
