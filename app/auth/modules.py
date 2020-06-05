import re
import sqlalchemy

from flask import flash, current_app
from flask_login import current_user
from werkzeug.security import check_password_hash
from datetime import datetime
from app.models import User, Role, ChangeLog
from app import db

def check_password_requirements(email, old_password, password, password_confirmation):
    """
    Check a password against security requirements.

    :param email: Email of user
    :param old_password: Original password
    :param password: Password that needs to be checked.
    :param password_confirmation: Confirmation of new password
    :return: Whether or not the new password is valid [Boolean]
    """

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
            "{} tried to change their password but failed: new password missing uppercase letter "
            "or number".format(current_user.email)
        )
        flash(
            "Your new password must contain eight characters and at least one uppercase letter and one number",
            category="warning",
        )
        return False

    return True