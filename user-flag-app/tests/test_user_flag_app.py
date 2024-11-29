import unittest
from user_flag_app import DatabaseManager


class TestDatabaseManager(unittest.TestCase):

    def setup(self):
        # Initialize DatabaseManager
        self.db_manager = DatabaseManager(":memory:")
        self.db_manager.initialize()

    def test_store_user_activity(self):
        """Test storing user activity with user_id, translated message and score."""
        user_id = 28391030
        translated_message = "This is a translated message."
        score = 0.22047281478907145

        try:
            self.db_manager.store_user_activity(user_id, translated_message, score)
            result = True
        except Exception as e:
            result = False
            print(f"Error occurred: {e}")

        self.assertTrue(result, "Failed to store user activity with translated message, etc.")


if __name__ == '__main__':
    unittest.main()