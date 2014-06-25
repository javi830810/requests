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

        user_registration = Request.query(Request.type == 'user_registered').order(Request.date).fetch()
        course_registration = Request.query(Request.type == 'course_registration').order(Request.date).fetch()
        challenge_exam_graded = Request.query(Request.type == 'challenge_exam_graded').order(Request.date).fetch()
        quiz_graded = Request.query(Request.type == 'quiz_graded').order(Request.date).fetch()

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render({
            'user_registration': self.pretty_print(user_registration),
            'course_registration': self.pretty_print(course_registration),
            'challenge_exam_graded': self.pretty_print(challenge_exam_graded),
            'quiz_graded': self.pretty_print(quiz_graded),
        }))

    def pretty_print(self, requests):
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
            result[y[0]] = y[1]

        return result


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/show', ShowOffHandler)
], debug=True)
