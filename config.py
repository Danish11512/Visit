import os

class Config():
    SECRET_KEY = (os.environ.get("SECRET_KEY") or "cityofnewyorkkeythatissecretandhardtoguess")
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (os.environ.get("DATABASE_URL") or "postgresql://developer@127.0.0.1:5432/visit_dev")
    EMAIL_DOMAIN = 'records.nyc.gov'
    

    
