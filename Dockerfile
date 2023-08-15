###########
# BUILDER #
###########

FROM arm64v8/python:3.11-slim-bullseye as builder

WORKDIR /builder

USER root

RUN apt-get update && apt-get install -y curl
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

COPY package*.json ./

RUN npm install

COPY . .

# Build the frontend dependencies
RUN npm run build
RUN npm run build-mail


#########
# FINAL #
#########

FROM arm64v8/python:3.11-slim-bullseye

ENV FLASK_APP wsgi.py
ENV FLASK_ENV production

RUN adduser --disabled-password --gecos "" server_runner

WORKDIR /opt/webapp

USER root

COPY --chown=server_runner:server_runner app app
COPY --chown=server_runner:server_runner migrations migrations
COPY --chown=server_runner:server_runner wsgi.py config.py boot.sh requirements.txt ./

RUN apt-get update && apt-get install -y cron nano sqlite3

RUN echo "0 * * * * cd /opt/webapp/ && . .venv/bin/activate && . ./project_env.sh && flask execute-job >> /opt/webapp/logs/pihole_job.log 2>&1" >> /etc/cron.d/webapp-cron \
    && echo "30 12 * * 0 cd /opt/webapp/ && . .venv/bin/activate && . ./project_env.sh && flask execute-weekly-notifications >> /opt/webapp/logs/weekly_email_job.log 2>&1" >> /etc/cron.d/webapp-cron \
    && crontab -u server_runner /etc/cron.d/webapp-cron \
    && mkdir -p /opt/webapp/logs \
    && touch /opt/webapp/logs/pihole_job.log /opt/webapp/logs/weekly_email_job.log \
    && chown server_runner:server_runner /opt/webapp/logs/pihole_job.log /opt/webapp/logs/weekly_email_job.log \
    && chmod u+s /usr/sbin/cron

RUN chown -R server_runner:server_runner /opt/webapp
RUN chmod u+x /opt/webapp/boot.sh

USER server_runner

RUN mkdir -p /opt/webapp/data/rel_db
RUN mkdir -p /opt/webapp/data/pihole_etc

# Copy built files from the builder stage
COPY --from=builder --chown=server_runner:server_runner /builder/app/static/dist /opt/webapp/app/static/dist

RUN python -m venv .venv
RUN .venv/bin/pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["./boot.sh"]
