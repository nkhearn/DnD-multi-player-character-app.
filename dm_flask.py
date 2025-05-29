from flask import Flask, render_template, request, redirect, url_for
from flask_httpauth import HTTPBasicAuth # Import the authentication library
from werkzeug.security import generate_password_hash, check_password_hash # For password hashing
import os
import json
# qr code imports
import qrcode
import io
import base64
from urllib.parse import urlparse
from PIL import Image
# end qr

# Assuming the provided class is saved in a file named dnd_character.py
from dnd import dnd_character

# Specify the template and static folders
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
character_dir = 'characters' # Use a variable for the character directory

# Check if directories exist, create if not
if not os.path.exists(template_dir):
    os.makedirs(template_dir)
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
if not os.path.exists(character_dir):
    os.makedirs(character_dir)

def generate_qr_code_image(url_data: str) -> Image.Image:
    """
    Generates a QR code image for the given URL data.

    Args:
        url_data: The string data (URL) to encode in the QR code.

    Returns:
        A Pillow Image object representing the QR code.
    """
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,  # Controls the size of the QR code (1 to 40)
        error_correction=qrcode.constants.ERROR_CORRECT_L, # About 7% or fewer errors can be corrected
        box_size=10, # How many pixels each box of the QR code is
        border=4, # How many boxes thick the border should be
    )

    # Add the URL data
    qr.add_data(url_data)
    qr.make(fit=True)  # Compile the data into a QR code array

    # Create an image from the QR code array
    img = qr.make_image(fill_color="black", back_color="white")

    return img

def image_to_base64_data_url(image: Image.Image) -> str:
    """
    Converts a Pillow Image object to a base64 encoded data URL (PNG format).

    Args:
        image: The Pillow Image object.

    Returns:
        A string representing the base64 data URL.
    """
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"



app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['SECRET_KEY'] = 'a_secret_key_for_security' # Change this to a real secret key

# --- Basic Authentication Setup ---
auth = HTTPBasicAuth()

# *** IMPORTANT SECURITY NOTE ***
# Hardcoding the username and password like this is NOT secure for production.
# For a real application, use environment variables, a configuration file
# outside the code, or a database to store hashed passwords.
# Remember to change "your_super_secret_password" to a strong password
users = {
    "dm": generate_password_hash("password")
}

@auth.verify_password
def verify_password(username, password):
    """
    Verifies the provided username and password.
    """
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None

# --- End Basic Authentication Setup ---


def get_character_list():
    """Gets a list of character names from the characters directory (.chr files)."""
    # Look for .chr files instead of .json
    character_files = [f for f in os.listdir(character_dir) if f.endswith('.chr')]
    # Extract names, converting filename like "blubba_da_moo.chr" back to "Blubba Da Moo"
    character_names = [f.replace('.chr', '').replace('_', ' ').title() for f in character_files]
    return character_names

@app.route('/')
@auth.login_required # Protect this route with basic authentication
def index():
    """Displays a list of all characters."""
    characters = get_character_list()
    return render_template('indexdm.html', characters=characters)

@app.route('/create_character', methods=['POST'])
@auth.login_required # Protect this route
def create_character():
    """Handles the creation of a new character."""
    base_name = "New Adventurer"
    new_character_name = base_name
    counter = 1
    # Generate a unique name by appending a number if needed
    while os.path.exists(os.path.join(character_dir, f"{new_character_name.lower().replace(' ', '_')}.chr")):
        new_character_name = f"{base_name} {counter}"
        counter += 1

    # Create a new dnd_character instance with default values
    new_character = dnd_character(name=new_character_name)

    # Save the new character to a file
    save_success, save_messages = new_character.save(character_dir)

    if not save_success:
        print(f"Error creating new character {new_character_name}: {save_messages}")
        # In a real app, you might want to flash an error message to the user
        return redirect(url_for('index')) # Redirect back to index on error

    # Redirect to the new character's edit page
    return redirect(url_for('view_character', character_name=new_character.name))


@app.route('/character/<character_name>', methods=['GET', 'POST'])
@auth.login_required # Protect this route with basic authentication
def view_character(character_name):
    """
    Displays and allows editing of a single character's details using the dnd_character class.
    Handles both GET (display) and POST (save) requests.
    Removes conditions with value 0 and inventory items with amount < 1 on save.
    """
    # Convert display name back to the name format used in the filename
    filename_name_base = character_name.lower().replace(' ', '_')

    # Create a dnd_character instance and attempt to load data
    character = dnd_character(name=character_name) # Initialize with the display name
    load_success, load_messages = character.load(character_dir) # Attempt to load from file

    # If loading failed for a GET request, it means the character file doesn't exist,
    # so redirect to index.
    if request.method == 'GET' and not load_success and 'name' not in character.__dict__:
         print(f"Error loading data for {character_name}. Redirecting to index. Messages: {load_messages}")
         return redirect(url_for('index'))

    # If loading failed for a POST request, it's an error state, perhaps the file was deleted
    # during editing. We can log the error and redirect.
    if request.method == 'POST' and not load_success and 'name' not in character.__dict__:
         print(f"Error loading data for {character_name} during POST. Redirecting to index. Messages: {load_messages}")
         return redirect(url_for('index'))


    if request.method == 'POST':
        # Determine if an add button was clicked BEFORE processing other data
        add_inventory_clicked = 'add_inventory' in request.form
        add_condition_clicked = 'add_condition' in request.form

        # Update simple attributes directly from form data
        # Use .get() with default values to prevent errors if a field is missing
        character.name = request.form.get('name', character.name)
        try:
            character.max_health = int(request.form.get('max_health', character.max_health))
        except ValueError:
            print(f"Warning: Could not convert max_health '{request.form.get('max_health')}' to integer.")
            pass # Keep original value
        try:
            character._current_health = int(request.form.get('_current_health', character._current_health))
        except ValueError:
             print(f"Warning: Could not convert _current_health '{request.form.get('_current_health')}' to integer.")
             pass # Keep original value
        try:
            character.armour_class = int(request.form.get('armour_class', character.armour_class))
        except ValueError:
             print(f"Warning: Could not convert armour_class '{request.form.get('armour_class')}' to integer.")
             pass # Keep original value
        try:
            character.strength = int(request.form.get('strength', character.strength))
        except ValueError:
             print(f"Warning: Could not convert strength '{request.form.get('strength')}' to integer.")
             pass # Keep original value
        try:
            character.dexterity = int(request.form.get('dexterity', character.dexterity))
        except ValueError:
             print(f"Warning: Could not convert dexterity '{request.form.get('dexterity')}' to integer.")
             pass # Keep original value
        try:
            character.constitution = int(request.form.get('constitution', character.constitution))
        except ValueError:
             print(f"Warning: Could not convert constitution '{request.form.get('constitution')}' to integer.")
             pass # Keep original value
        try:
            character.intelligence = int(request.form.get('intelligence', character.intelligence))
        except ValueError:
             print(f"Warning: Could not convert intelligence '{request.form.get('intelligence')}' to integer.")
             pass # Keep original value
        try:
            character.wisdom = int(request.form.get('wisdom', character.wisdom))
        except ValueError:
             print(f"Warning: Could not convert wisdom '{request.form.get('wisdom')}' to integer.")
             pass # Keep original value
        try:
            character.charisma = int(request.form.get('charisma', character.charisma))
        except ValueError:
             print(f"Warning: Could not convert charisma '{request.form.get('charisma')}' to integer.")
             pass # Keep original value


        # --- Process structured conditions data ---
        updated_conditions = []
        j = 0
        while f'condition-{j}-name' in request.form:
            condition = {}
            condition_name = request.form.get(f'condition-{j}-name', '').strip()

            # Process the condition data regardless of name being empty
            condition['name'] = condition_name
            try:
                val_str = request.form.get(f'condition-{j}-value', '0').strip()
                try:
                    condition['value'] = float(val_str)
                except ValueError:
                    try:
                        condition['value'] = int(val_str)
                    except ValueError:
                        condition['value'] = 0
                        print(f"Warning: Could not convert value for condition index {j}")

            except ValueError:
                 condition['value'] = 0
                 print(f"Warning: Could not convert value for condition index {j}")

            condition['attribute'] = request.form.get(f'condition-{j}-attribute', '').strip()

            # Add to updated list only if value is not 0
            if condition['value'] != 0:
                 updated_conditions.append(condition)

            j += 1

        # If the 'Add Condition' button was clicked, append a new empty condition
        if add_condition_clicked:
            # Append a new empty condition structure with default values
            updated_conditions.append({"name": "", "value": 0, "attribute": ""})

        # Update the character's internal _conditions list directly
        character._conditions = updated_conditions


        # --- Process structured inventory data ---
        updated_inventory = []
        i = 0
        while f'inventory-{i}-name' in request.form:
            item = {}
            item_name = request.form.get(f'inventory-{i}-name', '').strip()

            # Process the item data regardless of name being empty
            item['name'] = item_name
            try:
                item['amount'] = int(request.form.get(f'inventory-{i}-amount', 0))
            except ValueError:
                item['amount'] = 0
                print(f"Warning: Could not convert amount for item index {i}")

            try:
                item['value'] = float(request.form.get(f'inventory-{i}-value', 0.0))
            except ValueError:
                 item['value'] = 0.0
                 print(f"Warning: Could not convert value for item index {i}")
            try:
                item['weight'] = float(request.form.get(f'inventory-{i}-weight', 0.0))
            except ValueError:
                 item['weight'] = 0.0
                 print(f"Warning: Could not convert weight for item index {i}")
            try:
                item['gold_value'] = float(request.form.get(f'inventory-{i}-gold_value', 0.0))
            except ValueError:
                 item['gold_value'] = 0.0
                 print(f"Warning: Could not convert gold_value for item index {i}")

            item['type'] = request.form.get(f'inventory-{i}-type', '').strip()

            # Add to updated list only if amount is 1 or more
            if item['amount'] >= 1:
                 updated_inventory.append(item)

            i += 1

        # If the 'Add Inventory' button was clicked, append a new empty item
        if add_inventory_clicked:
             # Append a new empty item structure with default values
             updated_inventory.append({"name": "", "amount": 1, "value": 0.0, "weight": 0.0, "gold_value": 0.0, "type": ""})

        # Update the character's internal _inventory list directly
        character._inventory = updated_inventory


        # Save the character's state using the dnd_character's save method
        # Use character.name here as it might have been updated via the form
        save_success, save_messages = character.save(character_dir)
        if not save_success:
            print(f"Error saving character {character.name}: {save_messages}")
            # Potentially add a flash message here to show the user the error

        # Redirect back to the character page after saving
        return redirect(url_for('view_character', character_name=character.name)) # Use character.name in case it was changed


    # For GET request, render the character details using the loaded character object
    # Pass the character object's attributes directly to the template
    # The template will access character.name, character._current_health, etc.
    
    # current_url = request.url
    
    current_url = request.url
    parsed_url = urlparse(current_url)
    # new_url = f"{parsed_url.scheme}://{parsed_url.netloc}/view/{character.name}"
    
    custom_port = "5001"  # Example port number
    new_url = f"{parsed_url.scheme}://{parsed_url.netloc.split(':')[0]}:{custom_port}/view/{character.name}"

    
    
    qr_image = generate_qr_code_image(new_url)
    qr_data_url = image_to_base64_data_url(qr_image)
    
    return render_template('character.html', character=character, qr_image_url=qr_data_url)


if __name__ == '__main__':
    # Run the app in debug mode (useful for development)
    # In production, you would use a more robust server like Gunicorn or uWSGI
    # Use threaded=True to handle multiple requests simultaneously (basic threading)
    app.run(debug=True, threaded=True, host="0.0.0.0")
