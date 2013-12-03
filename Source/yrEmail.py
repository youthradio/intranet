import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os

gmail_user = "scripts@youthradio.org"
gmail_pwd = "TrBDXGZ9"

def mail(to, subject, text):
    msg = MIMEMultipart()

    msg['From'] = gmail_user
    msg['Subject'] = subject
    msg['To'] = ", ".join(to)

    msg.attach(MIMEText(text, 'html'))

    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail_user, gmail_pwd)
    mailServer.sendmail(gmail_user, to, msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()
