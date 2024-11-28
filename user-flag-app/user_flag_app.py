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

import csv
import argparse
import requests

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


def get_arguments():
    """
    Parse and return the command-line arguments for the script.

    Returns:
         argparse.Namespace: The parsed arguments from the command line.
    """
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(
        description='''Content Moderation System (CMS) - The system scores comments to report users posting offensive content.''')
    parser.add_argument('--input-file',
                        '-I',
                        help='The location of the input file',
                        dest='input_file',
                        action='store',
                        default='')
    parser.add_argument('--output-file',
                        '-O',
                        help='The location of the output file',
                        dest='output_file',
                        action='store',
                        default='')
    args = parser.parse_args()
    return args


def get_input(file):
    """Read input data from a CSV file.

    Example:
        [
            {'user_id': '28391029', 'message': 'You are a fool'},
            {'user_id': '28391029', 'message': 'This looks like a delicious cake'},
            {'user_id': '73829111', 'message': 'Completely bonkers!'}
        ]
    """
    data = []
    with open(file, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)
    return data


def query_translation_service(message):
    """Send a message to the translation API and return the response."""
    url = "http://api-translation-service:7000"
    payload = {"message": message}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    return response.json()


def query_scoring_service(message):
    """Send a message to the scoring API and return the response."""
    url = "http://api-scoring-service:8000"
    payload = {"message": message}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    return response.json()


def main():
    """
    Main entry point for the Content Moderation System.

    ............
    """
    args = get_arguments()
    missing_file_args = [
        not args.input_file,
        not args.output_file,
    ]
    if any(missing_file_args):
        raise SystemExit(1)
    for row in get_input(args.input_file):
        translated_message = query_translation_service(row['message'])
        print(f'translated_message {translated_message}')
        calculated_score = query_scoring_service(translated_message['translated_message'])
        print(f'calculated_score {calculated_score}')


if __name__ == "__main__":
    main()
