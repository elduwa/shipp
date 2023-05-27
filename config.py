import os
from dotenv import load_dotenv


class Config:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    INFLUXDB_HOST = os.getenv('INFLUXDB_HOST')
    INFLUXDB_PORT = os.getenv('INFLUXDB_PORT')


class DevelopmentConfig(Config):
    DEBUG = True

    def __init__(self):
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(dotenv_path)


class ProductionConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
