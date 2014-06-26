import webapp2
import json
import os
import datetime
import urllib
from google.appengine.ext import ndb
import jinja2
import logging

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Request(ndb.Model):
    request = ndb.TextProperty()
    type = ndb.StringProperty()
    date = ndb.DateTimeProperty()


class JsonHandler(webapp2.RequestHandler):
    """
    Handles setting Content-Type to application/json
    and returning of consistently formatted JSON results.
    """
    def __init__(self, request, response):
        self.request_data = None
        super(JsonHandler, self).__init__(request, response)

    def dispatch(self):
        try:
            self.response.content_type = 'application/json'
            result = super(JsonHandler, self).dispatch()
            if result is not None:
                self.api_success(result)
        except Exception, e:
            if not self.response.status:
                self.error(500)
            self.handle_exception(e, False)

    def __render_json__(self, data):
        self.response.write(json.dumps(data))

    def api_success(self, data=None):
        self.response.status = 200
        self.__render_json__(data)

    def set_location_header(self, model):
        self.response.headers["Location"] = "{0}/{1}".format(self.request.path, model.key().id())

    def handle_exception(self, exception, debug):
        logging.exception(exception)
        self.__render_json__(exception.message)

    def _data(self):
        if self.request_data is None:
            data_string = self.request.body
            self.request_data = json.loads(data_string)
        return self.request_data

    def get_response(self):
        raise Exception("hello world")

class MainHandler(webapp2.RequestHandler):

    file = 'requests'

    def get(self):
        self.post()

    def post(self):
        request_db = Request()
        request_db.request = self.request.body
        request_db.date = datetime.datetime.now()
        request_db.type = self._get_request_type(self.request.body)
        request_db.put()

    def _get_request_type(self, body):
        try:
            type = self.request.get('action', None)
            if type:
                return type

            a = json.loads(body)
            return a.get('action',None)
        except:
            return ""


class ShowOffHandler(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render())


class EventListHandler(JsonHandler):

    def get(self, event):
        offset = self.request.get('offset', 0)
        page_size = self.request.get('size', 1000)

        result = Request.query(
            Request.type == event).\
            order(Request.date).\
            fetch(page_size, offset=offset)

        return self._pretty_print(result)

    def _pretty_print(self, requests):
        result = []
        for req in requests:
            request_dict = self.try_to_parse_json(req.request)
            if not request_dict:
                request_dict = self.try_to_parse_form(req.request)

            result.append(request_dict)
        return result

    def try_to_parse_json(self, request):
        try:
            return json.loads(request)
        except Exception, e:
            return {}

    def try_to_parse_form(self, request):
        vars = request.split('&')
        result = {}
        for x in vars:
            y = x.split('=')
            logging.info(y)
            result[y[0]] = urllib.unquote(y[1])

        return result


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/show', ShowOffHandler),
    webapp2.Route('/event/<event>', handler='main.EventListHandler', name='list', handler_method='get')
], debug=True)
