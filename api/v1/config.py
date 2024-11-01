import os


MAIL_SERVER='smtp'
MAIL_HOST='live.smtp.mailtrap.io'
MAIL_PORT=587
MAIL_USERNAME='api'
MAIL_PASSWORD=os.getenv('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER="no-reply@chaleapp.org"
MAIL_FROM_NAME="Chale Services"