import re
from ..models import User
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





def validate(userid):
    user = User.query.get(userid=id)
    user.validated = True
    db.session.add(user)
    db.session.commit()

