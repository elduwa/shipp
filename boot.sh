#!/bin/sh
source .venv/bin/activate

echo "Migrating database (if necessary)..."
while true; do
    flask deploy
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Deploy command failed, retrying in 5 secs...
    sleep 5
done
echo "Database migrated"

echo "Starting cron..."
cron
echo "cron started"

echo "Starting gunicorn..."
exec gunicorn -b :8000 --access-logfile - --error-logfile - run:app

