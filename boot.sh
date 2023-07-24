#!/bin/bash

source .venv/bin/activate

database_file="/opt/webapp/data/rel_db/sqlite.db"

if [ -f "$database_file" ]; then
    echo "Running deploy routine..."
    while true; do
        flask deploy
        if [ "$?" -eq "0" ]; then
            break
        fi
        echo "Deploy command failed, retrying in 5 secs..."
        sleep 5
    done
    echo "Database migrated"
fi

echo "Starting cron..."
cron
echo "Cron started"

echo "Creating env export script for cron..."
{
    echo "export FLASK_APP=\"$FLASK_APP\""
    echo "export FLASK_ENV=\"$FLASK_ENV\""
    echo "export SECRET_KEY=\"$SECRET_KEY\""
    echo "export API_SECRET_KEY=\"$API_SECRET_KEY\""
    echo "export SQLITE_URL=\"$SQLITE_URL\""
    echo "export PIHOLE_DB_URL=\"$PIHOLE_DB_URL\""
    echo "export INFLUXDB_ACTIVE=\"$INFLUXDB_ACTIVE\""
    echo "export INFLUXDB_URL=\"$INFLUXDB_URL\""
    echo "export INFLUXDB_AUTH_TOKEN=\"$INFLUXDB_AUTH_TOKEN\""
    echo "export INFLUXDB_ORG=\"$INFLUXDB_ORG\""
    echo "export INFLUXDB_BUCKET=\"$INFLUXDB_BUCKET\""
    echo "export PIHOLE_DOMAIN=\"$PIHOLE_DOMAIN\""
    echo "export PIHOLE_AUTH_TOKEN=\"$PIHOLE_AUTH_TOKEN\""
    echo "export MAIL_SERVER=\"$MAIL_SERVER\""
    echo "export MAIL_PORT=\"$MAIL_PORT\""
    echo "export MAIL_USERNAME=\"$MAIL_USERNAME\""
    echo "export MAIL_PASSWORD=\"$MAIL_PASSWORD\""
    echo "export SQLITE_TEST_URL=\"$SQLITE_TEST_URL\""
    echo "export SCHEDULER_TIMEINTERVAL=\"$SCHEDULER_TIMEINTERVAL\""
} > ./project_env.sh

chmod +x ./project_env.sh

echo "Starting gunicorn..."
exec gunicorn -b :8000 --access-logfile - --error-logfile - wsgi:app
