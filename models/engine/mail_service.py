# email_service.py

from flask_mail import Mail, Message

# Initialize Flask-Mail
mail = Mail()

def init_app(app):
    mail.init_app(app)

def send_email(subject, recipients, body, html_body=None, attachments=None):
    """
    Send an email with the specified subject, recipients, content, and optional attachments from a stream.

    Args:
        subject (str): Subject of the email.
        recipients (list): List of recipient email addresses.
        body (str): Plain text email content.
        html_body (str, optional): HTML email content.
        attachments (list, optional): List of tuples containing attachment details.
                                      Each tuple should be (filename, file_stream, mimetype).

    Returns:
        bool: True if email is sent successfully, False otherwise.
    """
    try:
        msg = Message(subject, recipients=recipients, sender='no-reply@chaleapp.org')
        msg.body = body
        if html_body:
            msg.html = html_body

        # Add attachments, if any
        if attachments:
            for filename, file_stream, mimetype in attachments:
                file_stream.seek(0)  # Ensure the stream is at the beginning
                msg.attach(filename, mimetype, file_stream.read())

        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
