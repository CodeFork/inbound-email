__author__ = 'russomi'
import logging

import webapp2
from google.appengine.api import memcache
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler


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

        :param mail_message:
        """
        logging.info("Received a message from: " + mail_message.sender)
