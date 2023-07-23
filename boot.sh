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
else
    echo "Creating database..."
    flask db create-all
    echo "Database created"
fi

echo "Starting cron..."
cron
echo "Cron started"

echo "Starting gunicorn..."
exec gunicorn -b :8000 --access-logfile - --error-logfile - run:app
