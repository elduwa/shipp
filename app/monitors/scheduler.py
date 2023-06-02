from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask import current_app


class Scheduler():

    def __init__(self, time_interval_secs=3600):
        self._time_interval_secs = time_interval_secs

    def __init_BackgroundScheduler(self):
        jobstores = {
            'default': SQLAlchemyJobStore(url=current_app.config["JOBSTORE_DB_URL"])
        }
        job_defaults = {
            'coalesce': True
        }

        return BackgroundScheduler(jobstores=jobstores, job_defaults=job_defaults)
