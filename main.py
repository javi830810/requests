#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import json
import os
import datetime
import urllib
from google.appengine.ext import ndb
import jinja2

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
        self.response.write(self._write_request())

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

    # def _write_request(self):
    #     request_string = '{'
    #     variables = self.request.arguments()
    #     if variables:
    #         for var in variables:
    #             request_string += """ "%s" : "%s", """ %(var, self.request.get(var, default_value=''))
    #     request_string += '}'
    #
    #     return request_string


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
        requests = []

        for req in requests:
            try:
                requests.append(json.load(req.body))
            except Exception, e:
                requests.append({'cant parse request': req.body})

        return requests

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/show', ShowOffHandler)
], debug=True)
