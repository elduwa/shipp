FROM arm64v8/python:3.11-slim-bullseye as builder

WORKDIR /builder

USER root

# Install Node.js and npm
RUN apt-get update && apt-get install -y curl
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

# Copy package.json and package-lock.json
COPY package*.json ./

# Install Node.js dependencies
RUN npm install

# Copy the rest of the source code
COPY . .

# Build the project
RUN npm run build


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

RUN echo "0 * * * * /opt/webapp/.venv/bin/flask execute-job > /opt/webapp/logs/pihole_job.log 2>&1" >> /etc/cron.d/webapp-cron \
    && echo "0 12 * * 0 /opt/webapp/.venv/bin/flask execute-weekly-notifications > /opt/webapp/logs/weekly_email_job.log 2>&1" >> /etc/cron.d/webapp-cron \
    && crontab -u server_runner /etc/cron.d/webapp-cron \
    && mkdir -p /opt/webapp/logs \
    && touch /opt/webapp/logs/pihole_job.log /opt/webapp/logs/weekly_email_job.log \
    && chown server_runner:server_runner /opt/webapp/logs/job.log /opt/webapp/logs/weekly_email_job.log \
    && chmod u+s /usr/sbin/cron

# Grant permissions to server_runner user for the /opt/webapp/ directory
RUN chown -R server_runner:server_runner /opt/webapp

# Switch back to non-root user
USER server_runner

# Copy built files from the builder stage
COPY --from=builder --chown=server_runner:server_runner /builder/app/static/dist /opt/webapp/app/static/dist

RUN python -m venv .venv
RUN .venv/bin/pip install -r requirements.txt

# run-time configuration
EXPOSE 8000

ENTRYPOINT ["./boot.sh"]

# CMD [".venv/bin/gunicorn", "--bind", "0.0.0.0:8000", "run:app"]
# If wanting to write to stdout instead of default logfile (configure logfile in application)
#CMD ["gunicorn", "-b", ":5000", "--access-logfile", "-", "--error-logfile", "-", "flasky:app"]