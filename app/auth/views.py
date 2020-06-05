from . import auth
from flask import Flask, render_template, redirect, url_for, flash, current_app
from ..models import User
from flask_login import login_required, login_user, logout_user, current_user
from .forms import LoginForm
from .modules import increase_login_attempt, reset_login_attempts


@auth.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():  
        user = User.query.filter_by(email= form.email.data).first()

        if user:
            if user.login_attempts < 3 : 
                if user.verify_password(form.password.data):
                    login_user(user)
                    current_app.logger.info("User {} logged in".format(user.id))
                    current_app.logger.info("User {} login attempts reset to 0".format(user.id))
                    reset_login_attempts(user)
                    return redirect(url_for("auth.index"))
                else:
                    increase_login_attempt(user)
                    current_app.logger.info("User {} failed to log in, login attempts increased to {}".format(user.id, user.login_attempts))
                    flash("Invalid username or password", category="error")
                    return redirect(url_for("auth.login"))
            else:
                current_app.logger.info("User {} has reached max login attempts".format(user.id))
                flash("You have reached the maximum number of log in attempts, contact an adminsitrator for more details", category="error")
                return redirect(url_for("auth.login"))
    return render_template('auth/login.html', form=form)



@auth.route('/')
@auth.route('/index', methods=["GET", "POST"])
@login_required
def index():
    flash("Logged in successfully")
    return render_template("auth/index.html", name=current_user.first_name)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    current_app.logger.info("User logged out")
    return redirect(url_for('auth.login'))


# @app.route('/signup')
# def signup():
#     return render_template('signup.html')

# @app.route('/dashboard')
# def dashboard():
#     return render_template('dashboard.html')

if __name__ == '__auth__':
    app.run(debug=True)
