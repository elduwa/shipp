import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header
from flask import render_template, current_app
from app.monitors.pihole_monitor import weekly_summary
from app.reporting.pihole_reports import figure_to_byte_img, create_stacked_bar_chart, create_horizontal_bar_chart
from app.models.database_model import User
from app.extensions import db


class EmailBuilder:
    def __init__(self):
        self.msg = MIMEMultipart('related')

    def with_subject(self, subject):
        self.msg['Subject'] = Header(subject, 'utf-8')
        return self

    def with_sender(self, sender):
        self.msg['From'] = sender
        return self

    def with_recipient(self, recipient):
        self.msg['To'] = recipient
        return self

    def with_html_content(self, html_content):
        self.msg.attach(MIMEText(html_content, 'html'))
        return self

    def with_text_content(self, text_content):
        self.msg.attach(MIMEText(text_content, 'plain'))
        return self

    def add_image(self, image: MIMEImage, content_id: str | None):
        if content_id is not None:
            image.add_header('Content-ID', f'<{content_id}>')
        self.msg.attach(image)
        return self

    def build(self):
        return self.msg


def create_weekly_email(user: User):
    recipient = user.email_address
    username = user.username

    text_content = "Your email client does not support HTML messages. " \
                   "Please use an email client that does."
    html_content = render_template('emails/weekly-summary.html', username=username)

    df = weekly_summary()
    img_1 = figure_to_byte_img(create_stacked_bar_chart(df))
    img_2 = figure_to_byte_img(create_horizontal_bar_chart(df))

    chart1 = MIMEImage(img_1, 'png')
    chart2 = MIMEImage(img_2, 'png')

    msg = (
        EmailBuilder()
        .with_subject('Weekly summary')
        .with_sender(current_app.config["MAIL_USERNAME"])
        .with_recipient(recipient)
        .with_html_content(html_content)
        .with_text_content(text_content)
        .add_image(chart1, "chart1")
        .add_image(chart2, "chart2")
        .build()
    )

    return msg


def send_email(msg: MIMEMultipart):
    try:
        with smtplib.SMTP(current_app.config["MAIL_SERVER"], current_app.config["MAIL_PORT"]) as smtp:
            smtp.starttls()
            smtp.login(current_app.config["MAIL_USERNAME"], current_app.config["MAIL_PASSWORD"])
            smtp.send_message(msg)
    except smtplib.SMTPException as e:
        current_app.logger.error(f'Email not sent to {msg["To"]}. \n Error: {e}')

    current_app.logger.debug(f'Email sent to {msg["To"]}')
    return 'Sent'


def generate_weekly_emails():
    users = db.session.execute(db.select(User).where(User.email_address != None)).scalars().all() # noqa
    for user in users:
        msg = create_weekly_email(user)
        yield msg


def send_weekly_emails():
    for msg in generate_weekly_emails():
        send_email(msg)
