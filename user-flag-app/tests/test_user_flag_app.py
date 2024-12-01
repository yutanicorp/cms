import os
import csv
import pytest
import tempfile
from io import StringIO
from user_flag_app import DatabaseManager, ContentModerationSystem, MissingFileArgumentError


DB_PATH = 'test_database.sqlite3'

# Input data for the test in CSV format
in_mem_input_csv = StringIO("""\
user_id,message
28391029,"I don't believe the speaker!"
28391029,"I totally agree. Great video essay!"
42432992,"You can't make this up!"
""")

# Write the in-memory CSV to a temporary file
with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
    temp_file.write(in_mem_input_csv.getvalue().encode('utf-8'))
    temp_input_file_path = temp_file.name

# Expected data for assertions
expected_rows = [
    {"user_id": "28391029", "total_messages": 2},
    {"user_id": "42432992", "total_messages": 1}
]


@pytest.fixture(scope="module")
def cms_instance():
    db_manager = DatabaseManager(DB_PATH)
    db_manager.initialize()
    cms = ContentModerationSystem(db_manager)
    yield cms
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    if os.path.exists(temp_input_file_path):
        os.remove(temp_input_file_path)


def test_missing_file_arguments_exception(cms_instance):
    with pytest.raises(Exception) as exc:
        cms_instance.process(None, None)
    assert "Not enough file arguments provided. Both input and output files are required." in str(exc.value)
    assert exc.type == MissingFileArgumentError


def test_output_file_creation_and_contents(cms_instance):
    with tempfile.TemporaryDirectory() as temp_output_dir:
        temp_output_file_path = os.path.join(temp_output_dir, 'output.csv')

        cms_instance.process(temp_input_file_path, temp_output_file_path)

        assert os.path.exists(temp_output_file_path), "Output file was not created"

        with open(temp_output_file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)

            for i, row in enumerate(reader):
                expected_row = expected_rows[i]

                assert row["user_id"] == expected_row["user_id"]
                assert int(row["total_messages"]) == expected_row["total_messages"]

                avg_score = float(row["avg_score"])
                assert 0.0 <= avg_score <= 1.0, f"avg_score {avg_score} is out of range for user_id {row['user_id']}"
