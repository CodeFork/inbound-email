__author__ = 'russomi'

import unittest

import webapp2
import webtest
from google.appengine.api import mail
from google.appengine.ext import testbed
from google.appengine.api import memcache

from handlers.home import MainHandler
from handlers.home import CacheHandler


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)


class MailTestCase(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_mail_stub()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

    def tearDown(self):
        self.testbed.deactivate()

    def test_mail_sent(self):
        mail.send_mail(to='alice@example.com',
                       subject='This is a test',
                       sender='bob@example.com',
                       body='This is a test e-mail')

        messages = self.mail_stub.get_sent_messages(to='alice@example.com')

        self.assertEqual(1, len(messages))
        self.assertEqual('alice@example.com', messages[0].to)


class AppTest(unittest.TestCase):
    def setUp(self):
        app = webapp2.WSGIApplication([('/', MainHandler), ('/cache/', CacheHandler)])
        self.testapp = webtest.TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()

    def tearDown(self):
        self.testbed.deactivate()

    def test_hello_world_handler(self):
        response = self.testapp.get('/')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.normal_body, 'Hello World!')
        self.assertEqual(response.content_type, 'text/plain')

    def test_cache_handler(self):
        # First define a key and value to be cached.
        key = 'answer'
        value = '42'
        self.testbed.init_memcache_stub()
        params = {'key': key, 'value': value}
        # Then pass those values to the handler.
        response = self.testapp.post('/cache/', params)
        # Finally verify that the passed-in values are actually stored in Memcache.
        self.assertEqual(value, memcache.get(key))
        self.assertIsNotNone(response, msg='response is none!')


if __name__ == '__main__':
    unittest.main()
