FROM arm64v8/python:3.11-slim-bullseye

ENV FLASK_APP run.py
ENV FLASK_ENV production

# Create a non-root user
RUN adduser --disabled-password --gecos "" server_runner

WORKDIR /opt/webapp

# Switch to root user and install cron
USER root

COPY --chown=server_runner:server_runner app app
COPY --chown=server_runner:server_runner migrations migrations
COPY --chown=server_runner:server_runner nginx nginx
COPY --chown=server_runner:server_runner run.py config.py boot.sh requirements.txt ./

RUN apt-get update && apt-get install -y cron

RUN echo "0 * * * * /opt/webapp/.venv/bin/flask execute_job > /opt/webapp/logs/job.log 2>&1" >> /etc/cron.d/webapp-cron \
    && crontab -u server_runner /etc/cron.d/webapp-cron \
    && mkdir -p /opt/webapp/logs \
    && touch /opt/webapp/logs/job.log \
    && chown server_runner:server_runner /opt/webapp/logs/job.log \
    && chmod u+s /usr/sbin/cron

# Grant permissions to server_runner user for the /opt/webapp/ directory
RUN chown -R server_runner:server_runner /opt/webapp

# Switch back to non-root user
USER server_runner

RUN python -m venv .venv
RUN .venv/bin/pip install -r requirements.txt

# run-time configuration
EXPOSE 8000

ENTRYPOINT ["./boot.sh"]

# CMD [".venv/bin/gunicorn", "--bind", "0.0.0.0:8000", "run:app"]
# If wanting to write to stdout instead of default logfile (configure logfile in application)
#CMD ["gunicorn", "-b", ":5000", "--access-logfile", "-", "--error-logfile", "-", "flasky:app"]