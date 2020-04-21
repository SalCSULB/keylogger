from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

#import auth script
import auth
#Print lables from email for testing authentication
def get_labels():
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])

#Use mail.google.com to obtain the highest credentials to send attachements
SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'credentials.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'
#Get credentials for Authorization needed by API
authInst = auth.auth(SCOPES,CLIENT_SECRET_FILE,APPLICATION_NAME)
credentials = authInst.get_credentials()

http = credentials.authorize(httplib2.Http())
service = discovery.build('gmail', 'v1', http=http)

#import send_email class
import send_email

#SendInst sends the messages
#Pass in service to allow commands to server
sendInst = send_email.send_email(service)
#Message (our email credentials, reviever's email, email's subject, body text, screenshot file name)
#Sending email to our project email from our project email cecs378project@gmail.com   (Password is
message = sendInst.create_message_with_attachment('cecs378project@gmail.com','cecs378project@gmail.com','Testing 123','Hi there, This is a test from Python!', 'image.jpg' )
sendInst.send_message('me',message)