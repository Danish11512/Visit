from . import auth
from flask import Flask, render_template, redirect, url_for, flash, current_app,request
from ..models import User
from flask_login import login_required, login_user, logout_user, current_user
from .forms import LoginForm, ChangePasswordForm , PasswordResetRequestForm, PasswordResetForm
from .modules import increase_login_attempt, reset_login_attempts, check_previous_passwords, check_password_requirements,update_user_password
from app import db
from ..email_notification import send_email
from ..utils import InvalidResetToken

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
    return render_template('auth/login.html', form=form, reset_url=url_for("auth.password_reset_request"))



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

@auth.route("/reset", methods=["GET", "POST"])
def password_reset_request():
    """
    View function for requesting a password reset.

    :return: HTML page in which users can request a password reset.
    """
    current_app.logger.info("Start function password_reset_request() [VIEW]")
    if not current_user.is_anonymous:
        # If the current user is signed in, redirect them to TimeClock home.
        current_app.logger.info(
            "Current user ({}) is already signed in. Redirecting to index...".format(
                current_user.email
            )
        )
        return redirect(url_for("main.index"))

    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        current_app.logger.info(
            "Tried to submit a password reset request with account email {}".format(
                form.email.data
            )
        )
        current_app.logger.info(
            "Querying for user with given email: {}".format(form.email.data)
        )
        user = User.query.filter_by(email=form.email.data.lower()).first()
        current_app.logger.info("Finished querying for user with given email")
        if user:
            print("helloMunif")
            # If the user exists, generate a reset token and send an email containing a link to reset the user's
            # password
            token = user.generate_reset_token()
            send_email(
                user.email,
                "Reset Your Password",
                "auth/email/reset_password",
                user=user,
                token=token,
                next=request.args.get("next"),
            )
            current_app.logger.info(
                "Sent password reset instructions to {}".format(form.email.data)
            )
        flash(
            "If this account is in the system, an email with instructions to reset your password has been sent to you.",
            category="success",
        )
        current_app.logger.info("Redirecting to /auth/login...")
        current_app.logger.info("End function password_reset_request() [VIEW]")
        return redirect(url_for("auth.login"))
    current_app.logger.info("End function password_reset_request() [VIEW]")
    return render_template("auth/request_reset_password.html", form=form)

@auth.route("/reset/<token>", methods=["GET", "POST"])
def password_reset(token):
    """
    View function after a user has clicked on a password reset link in their inbox.

    :param token: The token that is checked to verify the user's credentials.
    :return: HTML page in which users can reset their passwords.
    """
    current_app.logger.info("Start function password_reset [VIEW]")
    if not current_user.is_anonymous:
        # If a user is signed in already, redirect them to index
        current_app.logger.info(
            "{} is already signed in. redirecting to /index...".format(
                current_user.email
            )
        )
        current_app.logger.info("End function password_reset")
        return redirect(url_for("main.index"))
    form = PasswordResetForm()
    if form.validate_on_submit():
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            # Token has timed out
            current_app.logger.error("EXCEPTION (ValueError): Token no longer valid")
            flash("This token is no longer valid.", category="warning")
            current_app.logger.info("End function password_reset")
            return redirect(url_for("auth.login"))

        current_app.logger.error("Querying for user that corresponds to given token")
        user = User.query.filter_by(id=data.get("reset")).first()
        current_app.logger.error("Finished querying for user")

        if user is None:
            # If the user associated with the token does not exist, log an error and redirect user to index
            current_app.logger.error("Requested password reset for invalid account.")
            current_app.logger.info("End function password_reset")
            return redirect(url_for("main.index"))

        elif (
            check_password_hash(
                pwhash=user.password_list.p1, password=form.password.data
            )
            or check_password_hash(
                pwhash=user.password_list.p2, password=form.password.data
            )
            or check_password_hash(
                pwhash=user.password_list.p3, password=form.password.data
            )
            or check_password_hash(
                pwhash=user.password_list.p4, password=form.password.data
            )
            or check_password_hash(
                pwhash=user.password_list.p5, password=form.password.data
            )
        ):
            # If user tries to set password to one of last five passwords, flash an error and reset the form
            current_app.logger.error(
                "{} tried to change password. Failed: Used old password.".format(
                    user.email
                )
            )
            flash(
                "Your password cannot be the same as the last 5 passwords",
                category="error",
            )
            current_app.logger.info("End function password_reset")
            return render_template("auth/reset_password.html", form=form)
        else:
            try:
                if (
                    "reset_token" in session
                    and session["reset_token"]["valid"]
                    and user.reset_password(form.password.data)
                ):
                    # If the token has not been used and the user submits a proper new password, reset users password
                    # and login attempts
                    user.login_attempts = 0
                    db.session.add(user)
                    db.session.commit()
                    session["reset_token"][
                        "valid"
                    ] = False  # Now that the token has been used, invalidate it
                    current_app.logger.error(
                        "Successfully changed password for {}".format(user.email)
                    )
                    flash("Your password has been updated.", category="success")
                    current_app.logger.info(
                        "End function password_reset... redirecting to login"
                    )
                    return redirect(url_for("auth.login"))

                elif "reset_token" in session and not session["reset_token"]["valid"]:
                    # If the token has already been used, flash an error message
                    current_app.logger.error(
                        "Failed to change password for {}: token invalid (already used)".format(
                            user.email
                        )
                    )
                    flash(
                        "You can only use a reset token once. Please generate a new reset token.",
                        category="error",
                    )
                    current_app.logger.info("End function password_reset")
                    return render_template("auth/reset_password.html", form=form)

                else:
                    if not "reset_token" in session:
                        flash(
                            "The reset token is timed out. Please generate a new reset token.",
                            category="error",
                        )
                    # Then the token is valid but the new password didn't meet minimum security criteria
                    else:
                        current_app.logger.error(
                            "Entered invalid new password for {}".format(user.email)
                        )
                        flash(
                            "Password must be at least 8 characters with at least 1 Uppercase Letter and 1 Number",
                            category="error",
                        )
                    current_app.logger.info("End function password_reset")
                    return render_template("auth/reset_password.html", form=form)

            except InvalidResetToken:
                current_app.logger.error(
                    "EXCEPTION (InvalidResetToken): Token no longer valid"
                )
                flash("This token is no longer valid.", category="warning")
                current_app.logger.info("End function password_reset")
                return redirect(url_for("auth.login"))

    current_app.logger.info("End function password_reset")
    return render_template("auth/reset_password.html", form=form)
if __name__ == '__auth__':
    app.run(debug=True)
