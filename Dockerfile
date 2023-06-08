FROM arm64v8/python:3.11-slim-bullseye

ENV FLASK_APP run.py
ENV FLASK_ENV production

# Create a non-root user
RUN useradd -ms /bin/bash server_runner

# Set the user for subsequent commands
USER server_runner

WORKDIR /app

COPY requirements.txt requirements.txt
RUN python -m venv .venv
RUN .venv/bin/pip install -r requirements.txt

COPY app app
COPY migrations migrations
COPY run.py config.py ./

# Switch to root user and install cron
USER root
RUN apt-get update && apt-get install -y cron

RUN echo "0 * * * * cd /app/app && .venv/bin/flask execute_job \>> job.log 2\>&1" > /etc/cron.d/webapp-cron

# Switch back to non-root user
USER server_runner

# run-time configuration
EXPOSE 8000
# If we rather use boot.sh approach
#ENTRYPOINT ["./boot.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "run:app"]
# If wanting to write to stdout instead of default logfile (configure logfile in application)
#CMD ["gunicorn", "-b", ":5000", "--access-logfile", "-", "--error-logfile", "-", "flasky:app"]