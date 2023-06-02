# Bundle all sections and expose the Flask APP
from flask import Flask
from config import Config
from app.monitors.pihole_monitor import fetch_query_data_job
from app.extensions import scheduler
import logging


def create_app(config: Config):
    appp = Flask(__name__)
    appp.config.from_object(config)

    appp.logger.setLevel(logging.INFO)

    appp.logger.info('starting app...')
    scheduler.init_app(appp)
    logging.getLogger("apscheduler").setLevel(logging.DEBUG)

    with appp.app_context():
        scheduler.add_job(id='pihole_monitor', func=fetch_query_data_job,
                          trigger='interval', seconds=appp.config['SCHEDULER_TIMEINTERVAL'])
        scheduler.start()

    # with appp.app_context():
     #   fetch_query_data_job()

    from app import views

    appp.register_blueprint(views.bp)

    return appp

# db_uri = app.config['SQLALCHEMY_DATABASE_URI']
# influxdb_host = app.config['INFLUXDB_HOST']

# move to model (see patterns in documentation) use current_app
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)
