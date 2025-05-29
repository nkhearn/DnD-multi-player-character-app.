from flask import Flask, render_template, jsonify
import os
import time # Import time for file timestamps
# Assuming the dnd_character class is in dnd_character.py
from dnd import dnd_character

# Specify the template and static folders
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
character_dir = 'characters' # Directory where character files are stored

# Ensure directories exist
if not os.path.exists(template_dir):
    os.makedirs(template_dir)
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
if not os.path.exists(character_dir):
    os.makedirs(character_dir)


app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Route to display character details
@app.route('/view/<character_name>')
def view_character(character_name):
    """
    Displays the details of a specific character.
    """
    # Convert display name to filename format
    filename_name_base = character_name.lower().replace(' ', '_')
    file_path = os.path.join(character_dir, f"{filename_name_base}.chr")

    # Create a dnd_character instance and attempt to load data
    character = dnd_character(name=character_name) # Initialize with the display name
    load_success, load_messages = character.load(character_dir) # Attempt to load from file

    if not load_success:
        # Handle case where character file is not found
        # You could render an error template or redirect
        return f"Character '{character_name}' not found.", 404 # Simple error message

    # Render the viewer template, passing the character object
    return render_template('viewer.html', character=character)

# Route to get the last modified timestamp of a character file
@app.route('/last_modified/<character_name>')
def get_last_modified(character_name):
    """
    Returns the last modified timestamp of a character's .chr file.
    Used by client-side JavaScript for polling.
    """
    filename_name_base = character_name.lower().replace(' ', '_')
    file_path = os.path.join(character_dir, f"{filename_name_base}.chr")

    if os.path.exists(file_path):
        try:
            # Get the last modification time as a timestamp
            timestamp = os.path.getmtime(file_path)
            return jsonify(last_modified=timestamp)
        except Exception as e:
            print(f"Error getting file modification time for {character_name}: {e}")
            return jsonify(error="Could not get file modification time"), 500
    else:
        # Return not found if the file doesn't exist
        return jsonify(error="Character file not found"), 404

if __name__ == '__main__':
    # Run the app on port 5001
    # debug=True enables auto-reloading of the server when code changes,
    # but the client-side polling handles data file changes.
    app.run(debug=True, port=5001, threaded=True, host="0.0.0.0")