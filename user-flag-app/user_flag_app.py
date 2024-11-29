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

import sqlite3
import csv
import argparse
import requests

# Constants for Service URLs
TRANSLATION_SERVICE_URL = "http://api-translation-service:7000"
SCORING_SERVICE_URL = "http://api-scoring-service:8000"

# SQLite Database Path
DB_PATH = '/sqlite/cms.db'

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


def initialize_db():
    """Initialize the database by creating the 'user_activity' table."""
    with sqlite3.connect('/sqlite/cms.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                translated_message TEXT,
                calculated_score REAL
            )
        ''')
        cursor.execute('''
            DELETE FROM user_activity;
        ''')
        conn.commit()


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
    """Read input data from a CSV file as a generator.

    Example:
        [
            {'user_id': '28391029', 'message': 'You are a fool'},
            {'user_id': '28391029', 'message': 'This looks like a delicious cake'},
            {'user_id': '73829111', 'message': 'Completely bonkers!'}
        ]
    """
    try:
        with open(file, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                yield row
    except IOError as e:
        print(f"Error reading the input file {file}: {e}")
        raise SystemExit(1)
    except Exception as e:
        print(e)


def query_translation_service(message):
    """Send a message to the translation API and return the response."""
    payload = {"message": message}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(TRANSLATION_SERVICE_URL, json=payload, headers=headers)
        return response.json()
    except requests.RequestException as e:
        print(f"Error querying the translation service: {e}")
        return None


def query_scoring_service(message):
    """Send a message to the scoring API and return the response."""
    payload = {"message": message}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(SCORING_SERVICE_URL, json=payload, headers=headers)
        return response.json()
    except requests.RequestException as e:
        print(f"Error querying the translation service: {e}")
        return None


def store_user_activity(user_id, translated_message, calculated_score):
    """Store user and associated message into the SQLite3 database."""
    with sqlite3.connect('/sqlite/cms.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_activity (user_id, translated_message, calculated_score)
            VALUES (?, ?, ?)
        ''', (user_id, translated_message, calculated_score))
        conn.commit()


def fetch_user_activity():
    """Fetch and display all user activity records."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_activity')
        rows = cursor.fetchall()
        for row in rows:
            print(row)


def process_message(row):
    """Process each message row by translating, scoring, and storing."""
    user_id = int(row['user_id'])

    # Translate message
    translated_data = query_translation_service(row['message'])
    translated_message = translated_data.get('translated_message', '')

    # Score message
    score_data = query_scoring_service(translated_message)
    score = score_data.get('score', 0.0)

    # Store result
    store_user_activity(user_id, translated_message, score)


def generate_user_statistics():
    """Generate user statistics from the database.

    Example:
        [(28391029, 2, 0.30724699136956457),
        (42432992, 1, 0.5374862315762217),
        (73829111, 1, 0.9470547559483797)]
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT user_id as user_id,'
                       'count(translated_message) as total_messages,'
                       'avg(calculated_score) as avg_score '
                       'FROM user_activity '
                       'GROUP BY user_id ')
        rows = cursor.fetchall()
        return rows


def write_output(file, data):
    """Write the processed data to a CSV file."""
    converted_data = [
        {'user_id': user_id,
         'total_messages': total_messages,
         'avg_score': avg_score}
        for user_id, total_messages, avg_score in data
    ]
    try:
        with open(file, 'w', newline='', encoding='utf-8') as csv_file:
            fieldnames = ['user_id', 'total_messages', 'avg_score']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            for row_dict in converted_data:
                writer.writerow(row_dict)

        print(f"Data successfully written to {file}.")
    except IOError as e:
        print(f"Error writing to the output file {file}: {e}")
    except Exception as e:
        print(e)


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
        process_message(row)

    result = generate_user_statistics()
    write_output(args.output_file, result)


if __name__ == "__main__":
    initialize_db()
    main()
