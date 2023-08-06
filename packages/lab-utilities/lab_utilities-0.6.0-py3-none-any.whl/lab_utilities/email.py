# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 16:18:59 2023

@author: stefa
"""

import smtplib
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
import subprocess

def send_email(sender_email, sender_password, recipient_emails, subject, body):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        message = f"Subject: {subject}\n\n{body}"
        
        for r in recipient_emails:
            server.sendmail(sender_email, r, message)
        print(f'Email sent to {r}')
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        server.quit()
        
def get_email_by_name(name):
    with open('user_emails.json', 'r') as f:
        user_emails = json.load(f)
        try:
            return user_emails[name]
        except KeyError:
            print("User not added to user_emails.json")
            return None

def set_email_env_variables():
    bat_filename = 'set_email_env_vars.bat'
    package_path = os.path.dirname(__file__)
    script_path = os.path.join(package_path, bat_filename)
    subprocess.call([script_path])


def get_email_env_variables():
    email = os.environ.get('lab_utilities_email')
    password = os.environ.get('lab_utilities_email_password')

    return email, password


def email_error(recipients, subject, error):
    email_address, password = get_email_env_variables()
    send_email(email_address, password, recipients, subject, error)
