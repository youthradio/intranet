import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

import os

def mail(to, subject, text, gmail_user, gmail_pwd):
    msg = MIMEMultipart()

    msg['From'] = gmail_user
    msg['Subject'] = subject
    msg['To'] = ", ".join(to)

    msg.attach(MIMEText(text.encode('ascii', 'xmlcharrefreplace'), 'html'))

    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail_user, gmail_pwd)
    mailServer.sendmail(gmail_user, to, msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()
