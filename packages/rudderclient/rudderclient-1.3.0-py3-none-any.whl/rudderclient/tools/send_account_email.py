"""
Email sending library.

This library provides an easy way to send customizable emails with Python. 
It supports various kinds of attachments like images and PDF files.

Functions:
----------
get_image(file_path):
    Returns a MIMEImage object from a file path.

get_html(file_path, replacements):
    Returns a string from a file, replacing placeholders with actual values.

get_attachment(file_path, filename, _subtype):
    Returns a MIMEApplication object from a file path, filename, and MIME subtype.

send_email(SMTP_USERNAME, SMTP_PASSWORD, FROM, TO, SUBJECT, NAME, EMAIL, 
           PLATFORM='', ACCESS_URL='', PASSWORD='', FIRST_STEPS_FILE=None,
           ERROR=False):
    Sends an email using SMTP with the provided parameters.

    Parameters:
    ----------
    SMTP_USERNAME: str
        Username for the SMTP server.
    SMTP_PASSWORD: str
        Password for the SMTP server.
    FROM: str
        The email address that will appear as the sender of the email.
    TO: str
        The email address of the recipient.
    SUBJECT: str
        The subject of the email.
    NAME: str
        The name of the recipient.
    EMAIL: str
        The recipient's email, used in the email body.
    PLATFORM: str, optional
        The platform name, used in the email body.
    ACCESS_URL: str, optional
        The access URL, used in the email body.
    PASSWORD: str, optional
        The recipient's password, used in the email body.
    FIRST_STEPS_FILE: str, optional
        The file path of a PDF file to be attached to the email.
    ERROR: bool, optional
        Indicates if the email is an error email. If true, it changes the email template.

    Raises:
    -------
    Exception:
        If there is an error reading the images, processing the email template, or sending the email.
"""

import logging
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from smtplib import SMTP
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Working directory
WORKING_DIRECTORY = Path("./email_attach")
# AWS Config
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_PORT = 587
ATTACHMENT_PATH = WORKING_DIRECTORY / "attachments"


def get_image(file_path):
    with open(file_path, 'rb') as f:
        return MIMEImage(f.read())


def get_html(file_path, replacements):
    try:
        with open(file_path, 'r') as file:
            filedata = file.read()

        for key, val in replacements.items():
            filedata = filedata.replace(key, val)

        return filedata
    except Exception as e:
        logging.error(f"Error processing the email template: {e}")
        raise


def get_attachment(file_path, filename, _subtype):
    with open(file_path, 'rb') as f:
        attach = MIMEApplication(f.read(), _subtype=_subtype)
        attach.add_header('Content-Disposition', 'attachment', filename=str(filename))
        return attach
    
def send_email(SMTP_USERNAME, SMTP_PASSWORD, FROM, TO, SUBJECT, NAME, EMAIL, 
               PLATFORM='', ACCESS_URL='', PASSWORD='', FIRST_STEPS_FILE=None,
               ERROR=False):
    # AWS Config
    EMAIL_HOST_USER = SMTP_USERNAME
    EMAIL_HOST_PASSWORD = SMTP_PASSWORD

    msg = MIMEMultipart('alternative')
    msg['Subject'] = SUBJECT
    msg['From'] = FROM
    msg['To'] = TO

    # Attach Image
    try:
        logo_image = get_image(f'{ATTACHMENT_PATH}/logo.png')
        logo_image.add_header('Content-Disposition', 'attachment', filename="logo.png")
        logo_image.add_header('Content-ID', '<logo.png>')
        msg.attach(logo_image)

    except Exception as e:
        logging.error(f"Error reading the images: {e}")
        raise

    # Attach optional attachments
    if FIRST_STEPS_FILE:
        attach = get_attachment(FIRST_STEPS_FILE, 'first_steps.pdf', 'pdf')
        msg.attach(attach)
    
    # Adapt html and txt to user
    EMAIL_TEMPLATE_HTML = WORKING_DIRECTORY / ("error_email_template.html" if ERROR else "email_template.html")
    replacements = {
        '{{ EMAIL }}': EMAIL,
        '{{ NAME }}': NAME,
        '{{ PLATFORM }}': PLATFORM,
        '{{ ACCESS_URL }}': ACCESS_URL,
        '{{ PASSWORD }}': PASSWORD,
        '{{ COMPANY_NAME }}': "RealNaut",
        '{{ COMPANY_ADDRESS }}': "Calle de Arturo Soria, 122, 28043 Madrid",
        '{{ COMPANY_WEB }}': "www.realnaut.com"
    }

    try:
        filedata = get_html(EMAIL_TEMPLATE_HTML, replacements)
    except Exception as e:
        logging.error(f"Error processing the email template: {e}")
        raise

    msg.attach(MIMEText(filedata, 'html'))

    # Send Email
    try:
        with SMTP(host=EMAIL_HOST, port=EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.send_message(msg)

        logging.info(f"Email sent to {TO}")
    except Exception as e:
        logging.error(f"Error sending the email: {e}")
        raise
