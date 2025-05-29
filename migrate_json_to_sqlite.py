import os
import json
from dnd import dnd_character # Assuming dnd_character is in dnd.py
import database_setup # To ensure tables are created

# Constants
JSON_CHARACTER_DIR = 'characters'  # Directory where old .chr JSON files are stored
DB_PATH = 'dnd_characters.db'    # Path to the SQLite database

def migrate_json_to_sqlite():
    """
    Migrates character data from JSON .chr files to the SQLite database.
    """
    print(f"Starting migration from JSON files in '{JSON_CHARACTER_DIR}' to SQLite DB '{DB_PATH}'...")

    # Ensure the database and tables exist
    try:
        database_setup.create_tables() # create_tables might not take db_path, ensure it uses the default or is updated
        print(f"Database '{DB_PATH}' and tables ensured/created.")
    except Exception as e:
        print(f"Error ensuring database tables: {e}. Please check 'database_setup.py'.")
        return

    # Check if the JSON character directory exists
    if not os.path.exists(JSON_CHARACTER_DIR):
        print(f"Error: JSON character directory '{JSON_CHARACTER_DIR}' not found. No files to migrate.")
        return
    if not os.path.isdir(JSON_CHARACTER_DIR):
        print(f"Error: '{JSON_CHARACTER_DIR}' is not a directory.")
        return

    migrated_count = 0
    error_count = 0

    # Iterate through all files in the JSON_CHARACTER_DIR
    for filename in os.listdir(JSON_CHARACTER_DIR):
        if filename.endswith(".chr"):
            file_path = os.path.join(JSON_CHARACTER_DIR, filename)
            print(f"\nProcessing file: {file_path}...")

            try:
                with open(file_path, 'r') as f:
                    json_data = json.load(f)

                # Extract character name safely, use filename as fallback if 'name' key is missing
                char_name_from_json = json_data.get("name")
                if not char_name_from_json:
                    # Attempt to derive name from filename if not in JSON (e.g. "zaltar_the_merchant.chr" -> "Zaltar the Merchant")
                    char_name_from_filename = os.path.splitext(filename)[0].replace('_', ' ').title()
                    print(f"Warning: 'name' key not found in JSON for {filename}. Using filename-derived name: '{char_name_from_filename}'")
                    char_name = char_name_from_filename
                    if not char_name: # If filename itself was problematic
                         print(f"Error: Could not determine character name for {filename}. Skipping.")
                         error_count +=1
                         continue
                else:
                    char_name = char_name_from_json

                print(f"Attempting to migrate character: {char_name}")

                # Create a dnd_character instance
                # The dnd_character class should take db_path in its constructor
                character_to_migrate = dnd_character(name=char_name, db_path=DB_PATH)

                # Populate attributes from JSON data, using .get() for safety
                character_to_migrate.max_health = json_data.get("max_health", 100)
                # Important: _current_health is the key in JSON, current_health in DB table
                character_to_migrate._current_health = json_data.get("_current_health", character_to_migrate.max_health)
                character_to_migrate.armour_class = json_data.get("armour_class", 10)
                character_to_migrate.strength = json_data.get("strength", 10)
                character_to_migrate.dexterity = json_data.get("dexterity", 10)
                character_to_migrate.constitution = json_data.get("constitution", 10)
                character_to_migrate.intelligence = json_data.get("intelligence", 10)
                character_to_migrate.wisdom = json_data.get("wisdom", 10)
                character_to_migrate.charisma = json_data.get("charisma", 10)
                
                # Conditions and Inventory are stored as lists of dicts
                character_to_migrate._conditions = json_data.get("_conditions", [])
                character_to_migrate._inventory = json_data.get("_inventory", [])

                # Call the save method (which should now save to SQLite)
                save_success, save_messages = character_to_migrate.save()

                if save_success:
                    print(f"Successfully migrated '{char_name}' to SQLite database.")
                    migrated_count += 1
                else:
                    print(f"Failed to migrate '{char_name}'. Messages: {save_messages}")
                    error_count += 1

            except FileNotFoundError:
                print(f"Error: File '{file_path}' not found during iteration (should not happen if os.listdir is used). Skipping.")
                error_count += 1
            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON from '{file_path}'. File might be corrupted. Skipping.")
                error_count += 1
            except Exception as e:
                print(f"An unexpected error occurred while processing '{file_path}': {e}")
                error_count += 1
    
    print(f"\nMigration complete. {migrated_count} character(s) migrated successfully.")
    if error_count > 0:
        print(f"{error_count} character(s) failed to migrate or encountered errors.")

if __name__ == "__main__":
    migrate_json_to_sqlite()
