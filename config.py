import os

class Config():
    SECRET_KEY = (os.environ.get("SECRET_KEY") or "cityofnewyorkkeythatissecretandhardtoguess")
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or "postgresql://developer@127.0.0.1:5432/visit_dev"
    )
    EMAIL_DOMAIN = 'records.nyc.gov'
    ADMIN = os.environ.get("ADMIN") or "admin@records.nyc.gov"
    MAIL_SERVER = os.environ.get("MAIL_SERVER") or "localhost"
    MAIL_PORT = os.environ.get("MAIL_PORT") or 1111
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") or False
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME") or None
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD") or None
    MAIL_SUBJECT_PREFIX = "[Visit]"
    MAIL_SENDER = "Records Visit <admin@records.nyc.gov>"

    
