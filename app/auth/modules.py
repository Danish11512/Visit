from ..models import User
from app import db
from flask import current_app

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