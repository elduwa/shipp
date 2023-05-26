import os


class Config:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    INFLUXDB_HOST = os.getenv('INFLUXDB_HOST')
    INFLUXDB_PORT = os.getenv('INFLUXDB_PORT')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
