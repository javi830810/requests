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
        self.post(method='GET')

    def post(self, method="POST"):
        request_db = Request()
        request_db.request = self.get_request_formatted()
        request_db.date = datetime.datetime.now()
        request_db.type = method
        request_db.put()

    def get_request_formatted(self):

        request_string = 'REQUEST_HEADERS:\n'
        headers = self.request.headers
        if headers:
            for var in headers:
                request_string += "%s : %s\n"%(var, headers[var])

        request_string = 'REQUEST_QUERY_STRING:\n'

        variables = self.request.arguments()
        if variables:
            for var in variables:
                request_string += "%s : %s\n" %(var, self.request.get(var, default_value=None))

        request_string += "REQUEST_BODY:\n"
        request_string += self.request.body

        return request_string


class ShowOffHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render({
            'all': Request.query().order(-Request.date).fetch(99),
        }))

app = webapp2.WSGIApplication([
    ('/', ShowOffHandler),
    ('/event', MainHandler)

], debug=True)
