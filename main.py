import webapp2
#from webapp2_extras import jinja2
from google.appengine.ext import ndb
from handlers.home import MainHandler
from handlers.home import CacheHandler
from handlers.home import LogSenderHandler


routes = [('/', MainHandler),
          ('/cache', CacheHandler),
          ('/_ah/warmup', MainHandler),
          LogSenderHandler.mapping()]

config = {'webapp2_extras.sessions': {
    'secret_key': 'something-very-very-secret',
}}

app = ndb.toplevel(webapp2.WSGIApplication(routes=routes, debug=True, config=config))

