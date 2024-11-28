#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: app.py
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import random

"""
Main code for Content Moderation System (CMS).

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

__author__ = '''Vincent Schouten'''
__docformat__ = '''google'''
__date__ = '''28-11-2024'''
__copyright__ = '''Copyright 2024, Vincent Schouten'''
__license__ = '''MIT'''
__maintainer__ = '''Vincent Schouten'''
__email__ = '''<account@single.blue>'''
__status__ = '''Development'''  # "Prototype", "Development", "Production".


PORT = 8000


class RequestHandler(BaseHTTPRequestHandler):
    """Handles HTTP POST requests for scoring messages."""

    def do_POST(self):
        """Handle the POST request."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data)
            text = data.get('message', '')
            score = scoring(text)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            response = {'score': score}
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'error': str(e)}
            self.wfile.write(json.dumps(response).encode())


def scoring(text):
    """Calculate a random score for a given text message."""
    return random.uniform(0, 1)


def run(server_class=ThreadingHTTPServer, handler_class=RequestHandler, port=PORT):
    """Run the HTTP server."""
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()


if __name__ == '__main__':
    run()