from flask import Flask
from flask_mail import Mail, Message


class MailSender:

    def __init__(self, smtp_server, smtp_port, user, password, mail_recipients):
        self.__app = Flask(__name__)
        self.__app.config['MAIL_SERVER'] = smtp_server
        self.__app.config['MAIL_PORT'] = smtp_port
        self.__app.config['MAIL_USERNAME'] = user
        self.__app.config['MAIL_PASSWORD'] = password
        self.__app.config['MAIL_USE_TLS'] = False
        self.__app.config['MAIL_USE_SSL'] = True
        self.__mail_username = user
        self.__mail_recipients = mail_recipients
        self.__mail_client = Mail(self.__app)

    # return exception if occurred
    def send_mail(self, subject, body):
        try:
            msg = Message(
                sender=self.__mail_username,
                recipients=self.__mail_recipients,
                subject=subject,
                body=body)
            with self.__app.app_context():
                self.__mail_client.send(msg)
        except Exception as ex:
            return ex
