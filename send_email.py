from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

#Base64 for encoding the email
import base64
#each mime allows for each time of attachment
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import mimetypes
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

class send_email:
    def __init__(self,service):
        self.service = service
    def create_message(self,sender, to, subject, message_text):
      message = MIMEText(message_text)
      message['to'] = to
      message['from'] = sender
      message['subject'] = subject
      #Message only works if changed from string to bytes
      return {'raw': base64.urlsafe_b64encode(message.as_bytes())}

    def create_message_with_attachment(self,
        sender, to, subject, message_text, file):
      #needs multipart to make an extra part for each attachement
      message = MIMEMultipart()
      message['to'] = to
      message['from'] = sender
      message['subject'] = subject

      msg = MIMEText(message_text)
      message.attach(msg)

      content_type, encoding = mimetypes.guess_type(file)

      if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
      main_type, sub_type = content_type.split('/', 1)
      if main_type == 'text':
        fp = open(file, 'rb')
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
      elif main_type == 'image':
        fp = open(file, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
      elif main_type == 'audio':
        fp = open(file, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
      else:
        fp = open(file, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
      filename = os.path.basename(file)
      msg.add_header('Content-Disposition', 'attachment', filename=filename)
      message.attach(msg)
        #needs to be bytes with a .decode to change it back to plain 64 text
      return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    def send_message(self, user_id, message):
      """Send an email message.
      Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.
      Returns:
        Sent Message.
      """
      try:
        message = (self.service.users().messages().send(userId=user_id, body=message)
                   .execute())
        #brackets added for python 3 (delete them for python 2)
        print('Message Id: %s' % message['id'])
        return message
      #needs "as" and parentasis for python 3, use comma if python 2
      except errors.HttpError as error:
        print('An error occurred: %s' % error)