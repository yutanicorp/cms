#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: user_flag_app.py
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

import argparse
import csv
import logging.config
import sqlite3
import requests

# Constants for Service URLs
TRANSLATION_SERVICE_URL = "http://api-translation-service:7000"
SCORING_SERVICE_URL = "http://api-scoring-service:8000"

# SQLite Database Path
DB_PATH = '/sqlite/cms.db'

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                    )
LOGGER = logging.getLogger()
LOGGER_BASENAME = 'CMSLogger'


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


class MissingFileArgumentError(Exception):
    """Exception raised for missing input or output file arguments."""

    def __init__(self, message="Not enough file arguments provided. Both input and output files are required."):
        self.message = message
        super().__init__(self.message)


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
    return parser.parse_args()


class DatabaseManager:

    def __init__(self, db_path):
        self.db_path = db_path
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')

    def initialize(self):
        """
        Create the 'user_activity' table.

        Returns:
            None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_activity (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        translated_message TEXT,
                        calculated_score REAL
                    )
                ''')
                cursor.execute('DELETE FROM user_activity')
                conn.commit()
        except sqlite3.DatabaseError as e:
            self._logger.error(f"Database error occurred: {e}")
            raise

    def store_user_activity(self, user_id, translated_message, calculated_score):
        """
        Store user activity into the SQLite3 database.

        Arguments:
            user_id (int): User's ID.
            translated_message (str): The translated message.
            calculated_score (float): Scote of the message.

        Returns:
            None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user_activity (user_id, translated_message, calculated_score)
                    VALUES (?, ?, ?)
                ''', (user_id, translated_message, calculated_score))
                conn.commit()
            self._logger.debug(f"Stored activity for user_id: {user_id}, score: {calculated_score}.")
        except sqlite3.DatabaseError as e:
            self._logger.error(f"Database error occurred: {e}")
            raise

    def generate_user_statistics(self):
        """Generate user statistics from the database.

        Returns:
            list of tuples: Each tuple contains user_id, total_messages, avg_score.

        Example:
            [(28391029, 2, 0.30724699136956457),
            (42432992, 1, 0.5374862315762217),
            (73829111, 1, 0.9470547559483797)]
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT user_id, '
                               'count(translated_message) as total_messages, '
                               'avg(calculated_score) as avg_score '
                               'FROM user_activity '
                               'GROUP BY user_id')
                return cursor.fetchall()
        except sqlite3.DatabaseError as e:
            self._logger.error(f"Database error occurred: {e}")
            raise


class ContentModerationSystem:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self._logger = logging.getLogger(f'{LOGGER_BASENAME}.{self.__class__.__name__}')

    def _get_input(self, file):
        """Read input data from a CSV file as a generator.

        Arguments:
            file (str): The path to the CSV file to be read.

        Returns:
            generator: Yields each row from the CSV file as a dictionary.

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
                self._logger.debug(f"Finished reading the input file: {file}")
        except IOError as e:
            self._logger.error(f"Error reading the input file {file}: {e}")
            raise
        except TypeError as e:
            self._logger.error(f"Error reading the input file {file}: {e}")
            raise

    def _query_service(self, message, url):
        """
        Send a message to the translation or scoring API and return the response.

        Arguments:
            message (str): The message to be sent to the translation service.
            url (str): API endpoint URL

        Returns:
            dict or None: The JSON response from the translation service if successful;
                          None if an error occurs.
        """
        payload = {"message": message}
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, json=payload, headers=headers)
            self._logger.debug(f"Received response: {response} from {url}")
            return response.json()
        except requests.RequestException as e:
            self._logger.error(f"Error querying the service {url}: {e}")
            raise

    def _process_message(self, row):
        """
        Process each message row by translating, scoring, and storing.

        Arguments:
            row (dict): A dictionary containing 'user_id' and 'message', as provided in input file.

        Returns:
            None
        """
        user_id = int(row['user_id'])

        # Translating the message
        translated_data = self._query_service(row['message'], TRANSLATION_SERVICE_URL)
        translated_message = translated_data.get('translated_message', '')
        self._logger.debug(f"Successfully translated message for user_id: {user_id}")

        # Scoring the translated message
        score_data = self._query_service(translated_message, SCORING_SERVICE_URL)
        score = score_data.get('score', 0.0)
        self._logger.debug(f"Calculated score for user_id: {user_id} is {score}")

        # Storing the user activity
        self.db_manager.store_user_activity(user_id, translated_message, score)
        self._logger.debug(f"Activity stored for user_id: {user_id}")

    def _write_output(self, file, data):
        """
        Write the processed data to a CSV file.

         Arguments:
            file (str): The filepath where the CSV will be saved.
            data (list of tuples): The processed data to be written, each tuple contains
                                   (user_id, total_messages, avg_score).

        Returns:
            None
        """
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
            self._logger.debug(f"Data successfully written to {file}. "
                              f"Total records: {len(converted_data)}.")
        except IOError as e:
            self._logger.error(f"Error writing to output file {file}: {e}")
            raise

    def process(self, input_file, output_file):
        """
        Write the processed data to a CSV file.

         Arguments:
            input_file (str): The file path where the input CSV is located.
            output_file (str): The file path for the output CSV.

        Returns:
            None
        """
        self._logger.info(f"Starting to process the input file {input_file}.")
        if not input_file or not output_file:
            raise MissingFileArgumentError()
        for row in self._get_input(input_file):
            self._process_message(row)
        result = self.db_manager.generate_user_statistics()
        self._write_output(output_file, result)
        self._logger.info(f"Process completed successfully. Output written to {output_file}.")


def main():
    """
    Main entry point for the Content Moderation System.

    Processes input files containing user messages, scores them via API services,
    stores the results, performs analytics, and writes the output to a file.
    """
    try:
        args_input_file = get_arguments().input_file
        args_output_file = get_arguments().output_file

        db_manager = DatabaseManager(DB_PATH)
        db_manager.initialize()

        cms = ContentModerationSystem(db_manager)
        cms.process(args_input_file, args_output_file)
    except Exception as e:
        LOGGER.error(e)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
