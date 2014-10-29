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
        See: https://cloud.google.com/appengine/docs/python/mail/receivingmail
        See: https://blog.artooro.com/2012/04/04/how-to-handle-incoming-attachments-on-google-app-engine/
        See: https://gist.github.com/russomi/10d08bfb14841ffbcb55

        :param mail_message:
        """
        logging.info("Received a message from: " + mail_message.sender)

        # handle attachments
        if hasattr(mail_message, 'attachments'):
            for filename, filecontents in mail_message.attachments:
                logging.info('filename={}'.format(filename))
                bf = BlobFiles.new(filename, folder=GCS_UPLOAD_FOLDER)
                if bf:
                    bf.blob_write(filecontents.decode())
                    bf.put_async()
                    logging.info('Uploaded and saved in default GCS bucket: ' + bf.gcs_filename)


