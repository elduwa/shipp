import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    # Default application db
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLITE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PIHOLE_DOMAIN = os.getenv('PIHOLE_DOMAIN')
    PIHOLE_DB_URL = os.getenv('PIHOLE_DB_URL')
    PIHOLE_AUTH_TOKEN = os.getenv('PIHOLE_AUTH_TOKEN')
    INFLUXDB_ACTIVE = os.getenv('INFLUXDB_ACTIVE').lower() in ('true', '1', 't') if os.getenv(
        'INFLUXDB_ACTIVE') is not None else False
    INFLUXDB_URL = os.getenv('INFLUXDB_URL')
    INFLUXDB_AUTH_TOKEN = os.getenv('INFLUXDB_AUTH_TOKEN')
    INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET')
    INFLUXDB_ORG = os.getenv('INFLUXDB_ORG')
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    SCHEDULER_TIMEINTERVAL = os.getenv('SCHEDULER_TIMEINTERVAL')
    TZ = os.getenv('TZ')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    # Mounted pi-hole db
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_BINDS = {
        "pihole": os.getenv('PIHOLE_DB_URL')
    }


class ProductionConfig(Config):
    # Mounted pi-hole db
    SQLALCHEMY_BINDS = {
        "pihole": os.getenv('PIHOLE_DB_URL')
    }

    @classmethod
    def init_app(cls, app):
        pass


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLITE_TEST_URL')

    SQLALCHEMY_BINDS = {
        "pihole": os.getenv('PIHOLE_TEST_DB_URL')
    }


    @classmethod
    def init_app(cls, app):
        pass


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestConfig
}
