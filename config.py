import os

class Config():
    SECRET_KEY = os.environ.get("SECRET_KEY") or 'verysecretkey'
    DEBUG = True
    if os.environ.get('DATABSE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'postgresql://developer@127.0.0.1:5432/visit_dev'
    else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


    # SQLALCHEMY_DATABASE_URI = (
    #     os.environ.get("DATABASE_URI")
    #     or "postgresql://developer@127.0.0.1:5432/visit_dev"
    # )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EMAIL_DOMAIN = 'records.nyc.gov'
    ADMIN = os.environ.get("ADMIN") or "admin@records.nyc.gov"
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', True) == True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SUBJECT_PREFIX = os.environ.get('MAIL_SUBJECT_PREFIX')
    MAIL_DEFAULT_SENDER = ("Records Visit" , "appdev@records.nyc.gov")






checkin = {
    "Appointment Created": 0,
    "Guest Checked In": 1,
    "Guest Checked Out": 2, 
    "Appointment Cancelled": 3
}

departments = [
    ('Research','Research'),
    ('Genealogy','Genealogy')
]

roles = [
    ("User", "User"),
    ("Administrator", "Administrator")
] 
