import os
from dotenv import load_dotenv
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
# from cryptography.fernet import Fernet


class Config:

    DEBUG = False
    TESTING = False
    SQLITE_URI = os.getenv('SQLITE_URL')
    PIHOLE_DB_URL = os.getenv('PIHOLE_DB_URL')
    PIHOLE_AUTH_TOKEN = os.getenv('PIHOLE_AUTH_TOKEN')
    INFLUXDB_URL = os.getenv('INFLUXDB_URL')
    INFLUXDB_AUTH_TOKEN = os.getenv('INFLUXDB_AUTH_TOKEN')
    INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET')
    INFLUXDB_ORG = os.getenv('INFLUXDB_ORG')
    # JOBSTORE_DB_URL = os.getenv('JOBSTORE_DB_URL')
    # SCHEDULER_API_ENABLED = False
    # SCHEDULER_API_PREFIX = "/scheduler"
    # SCHEDULER_ENDPOINT_PREFIX = "scheduler."
    # SCHEDULER_ALLOWED_HOSTS = ["localhost"]
    # SCHEDULER_JOBSTORES = {
    #   'default': SQLAlchemyJobStore(url=JOBSTORE_DB_URL)
    # }
    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': True
    }
    SCHEDULER_TIMEINTERVAL = 3600


class DevelopmentConfig(Config):
    DEBUG = True

    def __init__(self):
        super().__init__()
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(dotenv_path)


class ProductionConfig(Config):
    pass


class TestConfig(Config):
    TESTING = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestConfig
}
