import os

class Config():
    SECRET_KEY = os.environ.get("SECRET_KEY") or 'verysecretkey'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or "postgresql://developer@127.0.0.1:5432/visit_dev"
    )
    EMAIL_DOMAIN = 'records.nyc.gov'
    ADMIN = os.environ.get("ADMIN") or "admin@records.nyc.gov"


checkin = {
    "Appointment Created": 0,
    "Guest Checked In": 1,
    "Guest Checked Out": 2
}

departments = [
    ('Research','Research'),
    ('Genealogy','Genealogy')
]

roles = [
    ("User", "User"),
    ("Administrator", "Administrator")
] 
