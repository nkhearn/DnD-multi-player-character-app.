import unittest
import os
import sqlite3
import sys

# Add project root to sys.path to allow imports from dnd, database_setup, character_viewer
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dnd import dnd_character
import database_setup
import character_viewer # Flask app for integration tests

# Define a test database path
TEST_DB_PATH = "test_dnd_characters.db"
ORIGINAL_DB_SETUP_NAME = database_setup.DB_NAME # Store original DB_NAME from database_setup
ORIGINAL_VIEWER_DB_PATH = character_viewer.DB_PATH # Store original DB_PATH from character_viewer

class TestDndSystem(unittest.TestCase):
    """
    Contains unit tests for the dnd_character class and
    integration tests for the character_viewer.py Flask application.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up the database once for all tests in this class.
        This involves creating a temporary test database and its schema.
        """
        # Override DB_PATH for character_viewer and database_setup for the duration of these tests
        character_viewer.DB_PATH = TEST_DB_PATH
        database_setup.DB_NAME = TEST_DB_PATH

        # Ensure a clean database for testing
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
        
        # print(f"Running setUpClass for TestDndSystem. DB_NAME in database_setup is now: {database_setup.DB_NAME}")
        database_setup.create_tables() # This will now use TEST_DB_PATH due to the override

    @classmethod
    def tearDownClass(cls):
        """
        Clean up the database after all tests in this class.
        Removes the temporary database file and resets overridden module variables.
        """
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
        
        # Reset overridden module variables to their original values
        database_setup.DB_NAME = ORIGINAL_DB_SETUP_NAME
        character_viewer.DB_PATH = ORIGINAL_VIEWER_DB_PATH
        # print(f"Running tearDownClass for TestDndSystem. DB_NAME in database_setup restored to: {database_setup.DB_NAME}")


    def setUp(self):
        """
        Runs before each test method.
        Ensures tables are empty for test isolation (character data).
        Sets up the Flask app client for integration tests.
        """
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()
        # Clear data from tables that store character-specific info
        cursor.execute("DELETE FROM characters")
        cursor.execute("DELETE FROM inventory")
        cursor.execute("DELETE FROM conditions")
        conn.commit()
        conn.close()

        # For integration tests: Set up the Flask app client
        character_viewer.app.testing = True # Enable Flask's test mode
        self.client = character_viewer.app.test_client()


    # --- Unit Tests for dnd_character ---

    def test_save_and_load_new_character(self):
        """
        Tests saving a new character and then loading it to verify data integrity.
        """
        char_to_save = dnd_character(name="Elara", max_health=120, armour_class=15,
                                     strength=14, dexterity=18, constitution=12,
                                     intelligence=10, wisdom=13, charisma=16,
                                     db_path=TEST_DB_PATH)
        char_to_save._current_health = 110
        char_to_save.add_item("Longbow", 1, 0, 2, 50, "Weapon")
        char_to_save.add_item("Arrows", 20, 0, 1, 1, "Ammunition")
        char_to_save.condition("Blessed", 1, "Attack Rolls")

        save_success, save_msg = char_to_save.save()
        self.assertTrue(save_success, f"Save failed: {save_msg}")

        char_to_load = dnd_character(name="Elara", db_path=TEST_DB_PATH)
        load_success, load_msg = char_to_load.load()
        self.assertTrue(load_success, f"Load failed: {load_msg}")

        self.assertEqual(char_to_load.name, "Elara")
        self.assertEqual(char_to_load.max_health, 120)
        self.assertEqual(char_to_load._current_health, 110)
        self.assertEqual(char_to_load.armour_class, 15)
        self.assertEqual(char_to_load.strength, 14)
        self.assertEqual(char_to_load.dexterity, 18)
        self.assertEqual(char_to_load.constitution, 12)
        self.assertEqual(char_to_load.intelligence, 10)
        self.assertEqual(char_to_load.wisdom, 13)
        self.assertEqual(char_to_load.charisma, 16)

        # Verify inventory (order might not be guaranteed, so check for presence and details)
        self.assertEqual(len(char_to_load._inventory), 2)
        loaded_longbow = next((item for item in char_to_load._inventory if item['name'] == "Longbow"), None)
        self.assertIsNotNone(loaded_longbow)
        self.assertEqual(loaded_longbow['amount'], 1)
        self.assertEqual(loaded_longbow['type'], "Weapon")

        loaded_arrows = next((item for item in char_to_load._inventory if item['name'] == "Arrows"), None)
        self.assertIsNotNone(loaded_arrows)
        self.assertEqual(loaded_arrows['amount'], 20)

        # Verify conditions
        self.assertEqual(len(char_to_load._conditions), 1)
        loaded_condition = char_to_load._conditions[0]
        self.assertEqual(loaded_condition['name'], "Blessed")
        self.assertEqual(loaded_condition['value'], 1)
        self.assertEqual(loaded_condition['attribute'], "Attack Rolls")

    def test_update_existing_character(self):
        """
        Tests saving, loading, modifying, saving again, and then loading to verify updates.
        """
        # Initial save
        char1 = dnd_character(name="Grom", max_health=150, strength=18, db_path=TEST_DB_PATH)
        char1._current_health = 100
        char1.add_item("Greataxe", 1, 0, 7, 20, "Weapon")
        char1.save()

        # Load and modify
        char2 = dnd_character(name="Grom", db_path=TEST_DB_PATH)
        char2.load()
        
        char2.health(-20) # Adjust health
        char2.add_item("Healing Potion", 2, 0, 0.5, 50, "Potion") # Add item
        char2.condition("Enraged", 2, "Strength") # Add condition
        
        save_success, save_msg = char2.save()
        self.assertTrue(save_success, f"Second save failed: {save_msg}")

        # Load again to verify changes
        char3 = dnd_character(name="Grom", db_path=TEST_DB_PATH)
        load_success, load_msg = char3.load()
        self.assertTrue(load_success, f"Third load failed: {load_msg}")

        self.assertEqual(char3._current_health, 80) # 100 - 20
        self.assertEqual(len(char3._inventory), 2)
        potion = next((item for item in char3._inventory if item['name'] == "Healing Potion"), None)
        self.assertIsNotNone(potion)
        self.assertEqual(potion['amount'], 2)
        
        self.assertEqual(len(char3._conditions), 1)
        self.assertEqual(char3._conditions[0]['name'], "Enraged")
        self.assertEqual(char3._conditions[0]['value'], 2)

    def test_load_nonexistent_character(self):
        """
        Tests that loading a character not in the database returns False.
        """
        char_nonexistent = dnd_character(name="Nobody", db_path=TEST_DB_PATH)
        success, messages = char_nonexistent.load()
        self.assertFalse(success)
        self.assertIn("Character 'Nobody' not found in database", messages[0]) # Check specific message

    # --- Integration Tests for character_viewer.py ---

    def _prepopulate_db_for_viewer(self, name, health_val, item_name, condition_name):
        """Helper to populate DB for viewer tests."""
        char = dnd_character(name=name, max_health=health_val, db_path=TEST_DB_PATH)
        char._current_health = health_val
        char.strength = 12 # Add a stat for checking
        if item_name:
            char.add_item(item_name, 1, 0, 1, 10, "TestItemType")
        if condition_name:
            char.condition(condition_name, 1, "TestAttribute")
        char.save()
        return char

    def test_view_existing_character(self):
        """
        Tests the /view/<character_name> route for an existing character.
        """
        char_name = "Borin Stonebeard"
        self._prepopulate_db_for_viewer(name=char_name, health_val=130, item_name="Warhammer", condition_name="Stunned")

        response = self.client.get(f'/view/{char_name}')
        self.assertEqual(response.status_code, 200)
        response_data = response.data.decode('utf-8')

        self.assertIn(char_name, response_data) # Check character name
        self.assertIn("130", response_data) # Check health
        self.assertIn("STR:", response_data) # Check a stat label
        self.assertIn("12", response_data) # Check Borin's strength value
        self.assertIn("Warhammer", response_data) # Check inventory item
        self.assertIn("Stunned", response_data) # Check condition

    def test_view_nonexistent_character(self):
        """
        Tests the /view/<character_name> route for a character that does not exist.
        """
        response = self.client.get('/view/NonExistentCharacterName123')
        self.assertEqual(response.status_code, 404)
        self.assertIn("Character 'NonExistentCharacterName123' not found.", response.data.decode('utf-8'))

if __name__ == '__main__':
    # This allows running the tests directly
    # Ensure character_viewer.DB_PATH and database_setup.DB_NAME are handled correctly
    # by setUpClass/tearDownClass if tests are run this way.
    print(f"Initial DB_NAME in database_setup: {database_setup.DB_NAME}")
    print(f"Initial DB_PATH in character_viewer: {character_viewer.DB_PATH}")
    unittest.main()
```
