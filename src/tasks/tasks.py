import smtplib
from email.message import EmailMessage
from celery import Celery
from config import SMTP_PASSWORD, SMTP_USER
from pydantic import EmailStr

# SMTP_HOST = "smtp.gmail.com"
SMTP_HOST = "smtp.yandex.ru"
SMTP_PORT = 465

celery = Celery('tasks', broker='redis://localhost:6379')

def get_email_template_dashboard(username: str, email_adr: EmailStr):
    email = EmailMessage()
    email['Subject'] = 'Ваш запрос принят в обработку!'
    email['From'] = SMTP_USER
    email['To'] = str(email_adr)

    email.set_content(
        '<div>'
        f'<h1 style="color: red;">Здравствуйте, {username}! Ваш запрос на добавление перевала принят в обработку.</h1>'
        '</div>',
        subtype='html'
    )
    return email


@celery.task
def send_email(username: str, email_adr: EmailStr):
    email = get_email_template_dashboard(username, email_adr)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(email)

