#!/bin/sh
source .venv/bin/activate

FILE=/opt/webapp/data/rel_db/sqlite.db
if [[ -f "$FILE" ]]; then
  echo "Migrating database..."
  while true; do
      flask deploy
      if [[ "$?" == "0" ]]; then
          break
      fi
      echo Deploy command failed, retrying in 5 secs...
      sleep 5
  done
  echo "Database migrated"
fi

echo "Starting cron..."
cron
echo "cron started"

echo "Starting gunicorn..."
exec gunicorn -b :8000 --access-logfile - --error-logfile - run:app

