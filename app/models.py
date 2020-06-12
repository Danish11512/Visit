import re
from datetime import datetime

from flask import current_app, session
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class Permission:
    USER = 0x01  # 0b00000001
    ADMINISTER = 0x80  # 0b10000000


class Role(db.Model):

    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship("User", backref="role", lazy="dynamic")

    @staticmethod
    def insert_roles():
        roles = {
            "User": (Permission.USER, True),
            "Administrator": (0xFF, False),
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return "<Role %r>" % self.name


class User(UserMixin, db.Model):
    """
    Specifies properties and functions of a TimeClock User.
    """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    validated = db.Column(db.Boolean, default=False)
    login_attempts = db.Column(db.Integer, default=0)
   
    old_passwords = db.Column(db.Integer, db.ForeignKey("passwords.id"))

   


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config["ADMIN"]:
                self.role = Role.query.filter_by(permissions=0xFF).first()
                self.validated = True
            else:
                self.role = Role.query.filter_by(default=True).first()
        self.password_list = Password(
            p1="", p2="", p3="", p4="", p5="", last_changed=datetime.now()
        )

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        """
        Creates and stores password hash.
        :param password: String to hash.
        :return: None.
        """
        self.password_hash = generate_password_hash(password)

    # generates token with default validity for 1 hour
    def generate_reset_token(self, expiration=3600):
        """
        Generates a token users can use to reset their accounts if locked out.
        :param expiration: Seconds the token is valid for after being created (default one hour).
        :return: the token.
        """
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        session["reset_token"] = {"token": s, "valid": True}
        return s.dumps({"reset": self.id})

    def reset_password(self, new_password):
        """
        Resets a user's password.
        :param token: The token to verify.
        :param new_password: The password the user will have after resetting.
        :return: True if operation is successful, false otherwise.
        """
        # checks if the new password is at least 8 characters with at least 1 UPPERCASE AND 1 NUMBER
        if len(new_password) < 8:
            return False
        score = 0
        if re.search("\d+", new_password):
            # If the new password contains a digit, increment score
            score += 1
        if re.search("[a-z]", new_password) and re.search("[A-Z]", new_password):
            # If the new password contains lowercase and uppercase letters, increment score
            score += 1
        if score < 2:
            return False
        # If the password has been changed within the last second, the token is invalid.
        if (datetime.now() - self.password_list.last_changed).seconds < 1:
            current_app.logger.error(
                "User {} tried to re-use a token.".format(self.email)
            )
            raise InvalidResetToken
        self.password = new_password
        self.password_list.update(self.password_hash)
        db.session.add(self)
        return True


    def verify_password(self, password):
        """
        Checks user-entered passwords against hashes stored in the database.
        :param password: The user-entered password.
        :return: True if user has entered the correct password, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

    def can(self, permissions):
        """
        Checks to see if a user has access to certain permissions.
        :param permissions: An int that specifies the permissions we are checking to see whether or not the user has.
        :return: True if user is authorized for the given permission, False otherwise.
        """
        return (
            self.role is not None
            and (self.role.permissions & permissions) == permissions
        )

    def is_administrator(self):
        """
        Checks to see whether the user is an administrator.
        :return: True if the user is an administrator, False otherwise.
        """
        return self.can(Permission.ADMINISTER)

    def __repr__(self):
        return "<User %r>" % self.email


class Password(db.Model):
    __tablename__ = "passwords"
    id = db.Column(db.Integer, primary_key=True)
    p1 = db.Column(db.String(128))
    p2 = db.Column(db.String(128))
    p3 = db.Column(db.String(128))
    p4 = db.Column(db.String(128))
    p5 = db.Column(db.String(128))
    last_changed = db.Column(db.DateTime)
    users = db.relationship("User", backref="password_list", lazy="dynamic")

    def update(self, password_hash):
        self.p5 = self.p4
        self.p4 = self.p3
        self.p3 = self.p2
        self.p2 = self.p1
        self.p1 = password_hash
        self.last_changed = datetime.now()


class ChangeLog(db.Model):
    """
    A model that contains a list of changes made to a user account.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    changer_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship("User", foreign_keys=[user_id])
    changer = db.relationship("User", foreign_keys=[changer_id])
    timestamp = db.Column(db.DateTime)
    old = db.Column(db.String(128))
    new = db.Column(db.String(128))
    category = db.Column(db.String(128))


class AnonymousUser(AnonymousUserMixin):

    @staticmethod
    def can(self, permissions):
        return False

    @staticmethod
    def is_administrator(self):
        return False



login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))