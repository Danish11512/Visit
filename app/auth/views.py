from . import auth
import os
from flask import Flask, render_template, redirect, url_for, flash, current_app,request
from ..models import User, Role
from flask_login import login_required, login_user, logout_user, current_user
from .forms import LoginForm, ChangePasswordForm, PasswordResetForm, RegistrationForm, ChangeUserDataForm
from .modules import increase_login_attempt, reset_login_attempts, check_previous_passwords, check_password_requirements,update_user_password, update_user_information, get_changelog_by_user_id
from app import db, mail
from flask_mail import Message
from sqlalchemy.orm import sessionmaker
from ..decorators import admin_required
from app.utils import eval_request_bool
from ..email_notification import send_email

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
        # if the user is not validated they will be routed back to change password form 
        current_app.logger.info("{} visited index but is not validated. Redirecting to /auth/change_password".format(current_user.email))
        return redirect(url_for("auth.change_password"))
    else:   
        flash("Logged in successfully")
        current_app.logger.info("user {} logged in".format(current_user.email))
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


@auth.route("/user_list", methods=["GET", "POST"])
@admin_required
@login_required
def user_list():
    """
    Renders a page with the list of users on it and related data on them. Also includes edit button to direct to
    edit user page
    :return: user_list.html which lists all the users in the application
    """

    Session = sessionmaker(bind=db.engine)
    session = Session()
    active = eval_request_bool(request.args.get("active", "true"), True)
    list_of_users = []
    list_of_users_all = User.query.filter_by(is_active=active).all()

    if request.method == "GET":
        current_app.logger.info("Starting Search")
        entry = request.args.get("search_input", "")
        search_result_email = User.query.filter(
            User.email.ilike("%" + entry + "%")
        ).all()
        search_result_fname = User.query.filter(
            User.first_name.ilike("%" + entry.title() + "%")
        ).all()
        search_result_lname = User.query.filter(
            User.last_name.ilike("%" + entry.title() + "%")
        ).all()

        if not entry:
            list_of_users = list_of_users_all
        else:
            list_of_users = list(
                set(
                    search_result_email
                    + search_result_fname
                    + search_result_lname
                )
            )
    if not list_of_users:
        flash("No results found", category="error")
    # Pass in separate list of users with and without divisions
    return render_template(
        "auth/user_list.html",
        list_of_users=list_of_users,
        active_users=active,
    )


@auth.route("/user/<user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def user_profile(user_id):
    # Usernames are everything in the email before the @ symbol
    # i.e. for sdhillon@records.nyc.gov, username is sdhillon
    user = User.query.filter_by(id=user_id).first()
    form = ChangeUserDataForm()
    list_of_sups = [
        (user.id, user.email) for user in User.query.filter_by(is_supervisor=True).all()
    ] + [(0, "No Supervisor")]
    if user.supervisor:
        # If a user has a supervisor, then that supervisor should be selected by default
        list_of_sups.insert(
            0,
            list_of_sups.pop(
                list_of_sups.index((user.supervisor.id, user.supervisor.email))
            ),
        )
    form.supervisor_id.choices = list_of_sups
    if not user:
        # If no user like that exists then flash and send back to userlist page
        current_app.logger.info("No user with that id exists")
        flash("No user with id {} was found".format(user_id), category="error")
        return redirect(url_for("auth.user_list"))
    elif user.role.name == "Administrator" and user == current_user:
        # If user is admin, redirect to index and flash a message,
        # as admin should not be allowed to edit their own info through frontend.
        # This also avoids the issue that comes with the fact that admins don't have
        # a supervisor.
        flash("Admins cannot edit their own information.", category="error")
        current_app.logger.info("Admin trying to edit their own info, sending back")
        return redirect(url_for("auth.user_list"))

    if form.validate_on_submit():
        if user.id == form.supervisor_id.data:
            # A user cannot be their own super so they are have to be flashed
            current_app.logger.info("A user cannot be their own supervisor, please change")
            flash("A user cannot be their own supervisor. Please revise your supervisor ""field.",category="error",)
        else:
            # If everthing is normal and there are no errors then proceed to save and return back the page
            current_app.logger.info("User information updated")
            flash("User information has been updated", category="success")
            update_user_information(
                user,
                form.first_name.data,
                form.last_name.data,
                form.role.data,
                form.department.data,
                form.supervisor_id.data,
                form.is_supervisor.data,
                form.is_active.data,
            )
            current_app.logger.info(
                "{} updated information for {}".format(current_user.email, user.email)
            )
            flash("Information Updated", category="success")
            return redirect(url_for("auth.user_profile", user_id=user.id))
    else:
        # Pre-populate the form with current values
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.department.data = user.department
        form.is_supervisor.data = user.is_supervisor
        form.supervisor_id.data = user.supervisor.email if user.supervisor else 0
        form.is_active.data = user.is_active
        form.role.data = user.role.name
        current_app.logger.info("Populated form with user info")
    

    # For ChangeLog Table
    changes = get_changelog_by_user_id(user.id)

    page = request.args.get("page", 1, type=int)
    pagination = changes.paginate(page, per_page=10, error_out=False)
    changes = pagination.items
    name = user.first_name + " " + user.last_name

    return render_template(
        "auth/user_profile.html",
        user=user,
        form=form,
        changes=changes,
        pagination=pagination,
        name=name
    )


@auth.route("/user/reset/<user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def admin_reset(user_id):
    # There needs to be anew form that resets the password instead of changing it. Which means it doesn't ask for te old password but instead just resets it where the user can then log back in 
    user = User.query.filter_by(id=user_id).first()
    form = PasswordResetForm()
    if not user:
        flash("No user with id {} was found".format(user_id), category="error")
        current_app.logger.info("There was no user found, so nothing to reset") 
        return redirect(url_for("auth.user_list"))
    # After validation update the info for the user 
    if form.validate_on_submit():
        user.password_list.update(current_user.password_hash)
        user.password = form.password.data
        user.login_attempts = 0
        user.validated = True
        db.session.add(user)
        db.session.commit()
        current_app.logger.info("{current_user_email} updated the password for {updated_user}.".format(current_user_email=current_user.email, updated_user=user.email))
        flash("{} password has been updated.".format(user.email), category="success")
        return redirect(url_for("auth.user_list"))
    else:
        return render_template("auth/reset_password.html", form=form)
    

@auth.route("/register", methods=["GET", "POST"])
@login_required
@admin_required
def register():
    # The admin can register new users fro mhere if they meet the requirements in the form 
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower(), department=form.department.data).first()
        if user:
            # if user exist then flash and redirect
            current_app.logger.info("{} already exists.".format(user.email))
            flash("User {} already exists".format(user.email), category="error")
            return redirect(url_for("auth.register"))

        else:      
            user = User(
                email=form.email.data.lower(),
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                department=form.department.data,
                role=Role.query.filter_by(name=form.role.data).first(),
                is_supervisor=form.is_supervisor.data,
                validated=False
            )
            db.session.add(user)
            db.session.commit()
            current_app.logger.info("Successfully registered user {}, sending mail".format(user.email))
            flash("User successfully registered.", category="success")
            # send two emails, one to the admin who created the user and one to the user saying they have an account now
            send_email(to=current_user.email,
                        subject= "User Registered",
                        template="auth/email/user_register_admin",
                        admin_name=current_user.first_name,
                        user_email = user.email,
                        first_name=form.first_name.data,
                        last_name=form.last_name.data,
                        department=form.department.data,
                        role=Role.query.filter_by(name=form.role.data).first().name,
                        is_supervisor=form.is_supervisor.data
            )
            send_email(to=user.email,
                        subject= "User Registered",
                        template="auth/email/user_register_user",
                        user_email = user.email,
                        password=form.password.data,
                        first_name=form.first_name.data,
                        last_name=form.last_name.data,
                        department=form.department.data,
                        role=Role.query.filter_by(name=form.role.data).first().name,
                        is_supervisor=form.is_supervisor.data
            )
            return redirect(url_for("auth.register"))
    return render_template("auth/register.html", form=form)


if __name__ == '__auth__':
    app.run(debug=True) 