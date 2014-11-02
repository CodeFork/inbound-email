__author__ = 'russomi'
import logging

import webapp2
from google.appengine.api import memcache
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

from models.blob_files import BlobFiles

GCS_UPLOAD_FOLDER = '/attachments'

class MainHandler(webapp2.RequestHandler):
    def get(self):
        """


        """
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello World!')


class CacheHandler(webapp2.RequestHandler):
    def post(self):
        """


        """
        key = self.request.get('key')
        value = self.request.get('value')
        memcache.set(key, value)


class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        """
        The InboundEmailMessage object includes attributes to access other message fields:

        subject contains the message subject.
        sender is the sender's address e.g. "Nobody <nobody@example.com>".
        to is a comma-seperated list of the message's primary recipients e.g. "Joe <joe@example.com>, Bill <bill@example.com>".
        cc contains a comma-seperated list of the cc recipients e.g. "Joe <joe@example.com>, Bill <bill@example.com>".
        date returns the message date.
        attachments is a list of file attachments, possibly empty. Each value in the list is a tuple of two elements: the filename and the file contents.
        original is the complete message, including data not exposed by the other fields such as email headers, as a Python email.message.Message.


        See: https://cloud.google.com/appengine/docs/python/mail/receivingmail
        See: https://blog.artooro.com/2012/04/04/how-to-handle-incoming-attachments-on-google-app-engine/
        See: https://gist.github.com/russomi/10d08bfb14841ffbcb55

        :param mail_message:
        """
        logging.info("Received a message from: " + mail_message.sender)
        logging.info("subject: " + mail_message.subject)
        logging.info("to: " + mail_message.to)

        if hasattr(mail_message, 'cc'):
            logging.info("cc: " + mail_message.cc)

        logging.info("date: " + mail_message.date)

        html_bodies = mail_message.bodies('text/html')

        for content_type, body in html_bodies:
            logging.info('content_type: ' + content_type)
            decoded_body = body.decode()
            logging.info('decoded_body: ' + decoded_body)

        plaintext_bodies = mail_message.bodies('text/plain')

        for content_type, body in plaintext_bodies:
            logging.info('content_type: ' + content_type)
            decoded_body = body.decode()
            logging.info('decoded_body: ' + decoded_body)

        # handle attachments
        # attachments is a list of file attachments, possibly empty. Each value in the list is a tuple of two elements: the filename and the file contents.
        if hasattr(mail_message, 'attachments'):
            for filename, filecontents in mail_message.attachments:
                logging.info('attachment filename: ' + filename)
                bf = BlobFiles.new(filename, folder=GCS_UPLOAD_FOLDER)
                if bf:
                    bf.blob_write(filecontents.decode())
                    bf.put_async()
                    logging.info('Uploaded and saved in default GCS bucket: ' + bf.gcs_filename)

        # original is the complete message, including data not exposed by the other fields such as email headers, as a Python email.message.Message.
        logging.info('original: ')
        logging.info(mail_message.original.as_string())
