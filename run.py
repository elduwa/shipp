from app import create_app
from config import Config, config
import os

current_config: Config = None

if os.getenv('FLASK_ENV') == 'production':
    current_config = config['production']()
else:
    current_config = config['development']()

app = create_app(current_config)


@app.cli.command()
def execute_job():
    """Run scheduled job"""
    from app.monitors.pihole_monitor import fetch_query_data_job
    fetch_query_data_job()


if __name__ == '__main__':
    app.logger.info("Starting with app.run()..")
    app.run(debug=True, use_debugger=False, use_reloader=False, passthrough_errors=True)
