from flask import Flask, render_template, jsonify
import os
# Assuming the dnd_character class is in dnd.py (relative import if in same package)
from dnd import dnd_character

# Specify the template and static folders
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

# Define the path to the SQLite database
DB_PATH = "dnd_characters.db"

# Ensure template and static directories exist (character_dir is no longer needed)
if not os.path.exists(template_dir):
    os.makedirs(template_dir)
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Route to display character details
@app.route('/view/<character_name>')
def view_character(character_name):
    """
    Displays the details of a specific character by loading from the database.
    """
    # Create a dnd_character instance, providing the name and database path
    character = dnd_character(name=character_name, db_path=DB_PATH)
    
    # Attempt to load the character data from the database
    load_success, load_messages = character.load() # load() now uses self.db_path

    if not load_success:
        # Handle case where character is not found in the database
        # You could render an error template or redirect
        app.logger.warning(f"Character '{character_name}' not found in database. Messages: {load_messages}")
        return f"Character '{character_name}' not found.", 404

    # Log successful load for debugging
    app.logger.info(f"Successfully loaded character '{character_name}' from database.")
    app.logger.debug(f"Character data: {character.name}, Health: {character.health()[0]}")


    # Render the viewer template, passing the character object
    return render_template('viewer.html', character=character)

# The get_last_modified route is removed as it's no longer relevant for DB persistence.

if __name__ == '__main__':
    # It's good practice to ensure the database and tables exist before running the viewer.
    # This can be done by running database_setup.py separately,
    # or by adding a check here if desired (though typically setup is a separate step).
    # For this example, we assume database_setup.py has been run.
    
    # Check if the database file exists, if not, guide the user.
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database file '{DB_PATH}' not found.")
        print("Please run 'python database_setup.py' to create the database and tables before starting the viewer.")
        # Optionally, exit if the DB doesn't exist, or attempt to create it.
        # For simplicity, we'll just print an error and continue, Flask will likely fail at DB connection.
        # import sys
        # sys.exit(1)

    print(f"Starting Flask app. Ensure '{DB_PATH}' exists and is set up.")
    print(f"View characters at: http://localhost:5001/view/<character_name>")
    # Run the app on port 5001
    # debug=True enables auto-reloading of the server when code changes.
    app.run(debug=True, port=5001, threaded=True, host="0.0.0.0")