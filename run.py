from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from app import create_app
from config import Config, config
from flask_migrate import upgrade
from app.extensions import db, migrate
from app.models.database_model import Device, DeviceConfig, Policy

current_config: Config = None

if os.getenv('FLASK_ENV') == 'production':
    current_config = config['production']
else:
    current_config = config['development']

app = create_app(current_config)

migrate.init_app(app, db)


@app.cli.command()
def execute_job():
    """Run scheduled job"""
    from app.monitors.pihole_monitor import fetch_query_data_job
    fetch_query_data_job()


@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # migrate database to latest revision
    upgrade()


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Device=Device,
                DeviceConfig=DeviceConfig, Policy=Policy)


@app.cli.command()
def send_email():
    """Send test email"""
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.image import MIMEImage
    from email.header import Header
    from flask import render_template
    from app.monitors.pihole_monitor import dummy_weekly_summary
    from app.reporting.pihole_reports import figure_to_byte_img, create_stacked_bar_chart, create_horizontal_bar_chart

    # Create the email message
    msg = MIMEMultipart('related')
    msg['Subject'] = Header('Weekly summary', 'utf-8')
    msg['From'] = 'shift.info@gmx.ch'
    msg['To'] = 'elliott.d.wallace@gmail.com'

    # Create the HTML content
    html_content = render_template('emails/weekly-summary.html')

    # Load the image files
    df = dummy_weekly_summary()
    img_1 = figure_to_byte_img(create_stacked_bar_chart(df))
    img_2 = figure_to_byte_img(create_horizontal_bar_chart(df))

    # Attach the HTML content
    msg.attach(MIMEText(html_content, 'html'))

    # Attach the images
    chart1 = MIMEImage(img_1, 'png')
    chart1.add_header('Content-ID', '<chart1>')
    msg.attach(chart1)

    chart2 = MIMEImage(img_2, 'png')
    chart2.add_header('Content-ID', '<chart2>')
    msg.attach(chart2)

    # Send the email
    with smtplib.SMTP(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]) as smtp:
        smtp.starttls()
        smtp.login(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
        smtp.send_message(msg)

    return 'Sent'


if __name__ == '__main__':
    app.logger.info("Starting with app.run()..")
    app.run(debug=True, use_debugger=False, use_reloader=False, passthrough_errors=True)
