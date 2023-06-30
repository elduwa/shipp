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
    INFLUXDB_URL = os.getenv('INFLUXDB_URL')
    INFLUXDB_AUTH_TOKEN = os.getenv('INFLUXDB_AUTH_TOKEN')
    INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET')
    INFLUXDB_ORG = os.getenv('INFLUXDB_ORG')
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    SCHEDULER_TIMEINTERVAL = 3600

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


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


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestConfig
}
