import os

class Config():
    SECRET_KEY = (
        os.environ.get("SECRET_KEY") or "cityofnewyorkkeythatissecretandhardtoguess"
    )


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or "postgresql://timeclock_db@127.0.0.1:5432/visit_dev"
    )
    @staticmethod
    def init_app(app):
        pass


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or "postgresql://localhost:5432/visit_test"
    )


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or "postgresql://localhost:5432/visit_prod"
    )


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
