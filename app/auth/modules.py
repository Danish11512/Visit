import re
import sqlalchemy
from ..models import User, ChangeLog, Role
from datetime import datetime
from app import db
from flask import current_app, flash
from flask_login import current_user
from werkzeug.security import generate_password_hash,check_password_hash

def increase_login_attempt(user):
    if user:
        if user.login_attempts < 3:
            user.login_attempts += 1
            db.session.add(user)
            db.session.commit()


def reset_login_attempts(user):
    if user:
        user.login_attempts = 0
        db.session.add(user)
        db.session.commit()


def check_password_requirements(email, old_password, password, password_confirmation):

    user_password = User.query.filter_by(email=email.lower()).first().password_hash

    if not check_password_hash(pwhash=user_password, password=old_password):
        # If the user enters the wrong current password
        current_app.logger.info(
            "{} tried to change their password but failed: entered invalid old password".format(
                current_user.email
            )
        )
        flash("Your old password did not match", category="warning")
        return False
    if password != password_confirmation:
        current_app.logger.info(
            "{} tried to change their password but failed: passwords did not match".format(
                current_user.email
            )
        )
        return False

    # Use a score based system to ensure that users match password security requirements
    score = 0
    if re.search("\d+", password):
        # If the password contains a digit, increment score
        score += 1
    if re.search("[a-z]", password) and re.search("[A-Z]", password):
        # If the password contains lowercase and uppercase letters, increment score
        score += 1
    if score < 2:
        current_app.logger.info(
            "{} tried to change their password but failed: new password missing uppercase letter or number".format(current_user.email)
        )
        flash(
            "Your new password must contain eight characters and at least one uppercase letter and one number", category="warning",)
        return False

    return True 


def check_previous_passwords(userid, password):
    user = User.query.get(int(userid))
    if (check_password_hash(pwhash=user.password_list.p1, password=password)
        or check_password_hash(pwhash=user.password_list.p2, password=password)
        or check_password_hash(pwhash=user.password_list.p3, password=password)
        or check_password_hash(pwhash=user.password_list.p4, password=password)
        or check_password_hash(pwhash=user.password_list.p5, password=password)):
            # If the inputted password is one of the user's last five passwords , return True 
            return True 
    else:
         return False 


def update_user_password(userid, password):
    user = User.query.get(int(userid))
    user.password_list.update(user.password_hash)
    user.password_hash = generate_password_hash(password)
    db.session.add(user)
    db.session.commit()



def get_changelog_by_user_id(id):
    current_app.logger.info("Start function get_changelog_by_user_id()")
    current_app.logger.info("Querying for changes made to user with id {}".format(id))
    changes = ChangeLog.query.filter_by(user_id=id).order_by(
        sqlalchemy.desc(ChangeLog.timestamp)
    )
    current_app.logger.info("End function get_changelog_by_user_id()")
    return changes




def update_user_information(
    user,
    first_name_input,
    last_name_input,
    role_input,
    department_input,
    supervisor_id_input,
    is_supervisor_input,
    is_active_input,
    
):
    current_app.logger.info(
        "Start function update_user_information for {}".format(user.email)
    )
    if (
        first_name_input
        and first_name_input != ""
        and (user.first_name != first_name_input)
    ):
        change = ChangeLog(
            changer_id=current_user.id,
            user_id=user.id,
            timestamp=datetime.now(),
            category="FIRST NAME",
            old=user.first_name,
            new=first_name_input,
        )
        db.session.add(change)
        db.session.commit()
        user.first_name = first_name_input

    if (
        last_name_input
        and last_name_input != ""
        and (user.last_name != last_name_input)
    ):
        change = ChangeLog(
            changer_id=current_user.id,
            user_id=user.id,
            timestamp=datetime.now(),
            category="LAST NAME",
            old=user.last_name,
            new=last_name_input,
        )
        db.session.add(change)
        db.session.commit()
        user.last_name = last_name_input

    if role_input and role_input != user.role_id:
        new_role = Role.query.filter_by(name=role_input).first()
        if user.role != new_role:
            change = ChangeLog(
                changer_id=current_user.id,
                user_id=user.id,
                timestamp=datetime.now(),
                category="ROLE",
                old=user.role.name,
                new=new_role.name,
            )
            db.session.add(change)
            db.session.commit()
            user.role = Role.query.filter_by(name=role_input).first()

    if department_input and user.department != department_input:
        if user.department:
            old_department = user.department
        else:
            old_department = "None"
        change = ChangeLog(
            changer_id=current_user.id,
            user_id=user.id,
            timestamp=datetime.now(),
            category="DEPARTMENT",
            old=old_department,
            new=department_input,
        )
        db.session.add(change)
        db.session.commit()
        user.department = department_input

    if (user.supervisor_id != supervisor_id_input) and (
        supervisor_id_input != 0 or user.supervisor
    ):
        oldsup = User.query.filter_by(id=user.supervisor_id).first()
        sup = User.query.filter_by(id=supervisor_id_input).first()
        change = ChangeLog(
            changer_id=current_user.id,
            user_id=user.id,
            timestamp=datetime.now(),
            category="SUPERVISOR",
            old=None if (user.supervisor_id is None) else oldsup.email,
            new=None if supervisor_id_input == 0 else sup.email,
        )
        db.session.add(change)
        db.session.commit()
        user.supervisor = sup

    if is_supervisor_input is not None and (user.is_supervisor != is_supervisor_input):
        change = ChangeLog(
            changer_id=current_user.id,
            user_id=user.id,
            timestamp=datetime.now(),
            category="IS SUPERVISOR",
            old=user.is_supervisor,
            new=is_supervisor_input,
        )
        db.session.add(change)
        db.session.commit()
        user.is_supervisor = is_supervisor_input

    if is_active_input is not None and (user.is_active != is_active_input):
        change = ChangeLog(
            changer_id=current_user.id,
            user_id=user.id,
            timestamp=datetime.now(),
            category="IS ACTIVE",
            old=user.is_active,
            new=is_active_input,
        )
        db.session.add(change)
        db.session.commit()
        user.is_active = is_active_input

    db.session.add(user)
    db.session.commit()
    current_app.logger.info("User info updated in update_user_information()")

