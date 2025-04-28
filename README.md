# D\&D Character Manager

A web-based application for managing Dungeons & Dragons 5th Edition character sheets, built with Python and Flask. This project provides a core character data structure and two separate web interfaces: one for Dungeon Masters (DMs) to create and edit characters, and a read-only viewer for players or others.

## Features

This project is divided into three main parts:

1.  **`dnd.py` - The Core Character Class:**
    * Represents a D\&D 5e character with standard attributes (Strength, Dexterity, etc.), max health, current health, and armour class.
    * Manages character conditions (status effects) and allows applying their effects (currently focused on health adjustments).
    * Manages character inventory, tracking items by name, amount, value, weight, gold value (in £), and type.
    * Provides methods to save and load character data to/from `.chr` files using JSON.

2.  **`app.py` - DM Management Interface (Authenticated):**
    * A Flask web application for Dungeon Masters.
    * Requires basic HTTP authentication for access.
    * Lists all saved characters.
    * Allows creating new characters with default values.
    * Provides a form-based interface to view and edit all aspects of a character: attributes, health, armour class, conditions, and inventory.
    * Saves character changes back to the `.chr` file using the `dnd_character` class.
    * Handles adding/removing conditions and inventory items via the form.

3.  **`viewer_app.py` - Character Viewer (Read-Only):**
    * A separate Flask web application for viewing character sheets.
    * **No authentication required.** Intended for players or public viewing (use with caution depending on your network setup).
    * Displays a read-only view of a specific character's details.
    * Includes an API endpoint (`/last_modified/<character_name>`) that returns the last modification timestamp of a character file, designed to be used with client-side JavaScript for polling and potentially updating the view automatically when the DM makes changes.

## Setup

### Prerequisites

* Python 3.6 or higher
* `pip` (Python package installer)

### Installation

1.  Clone this repository:
    ```bash
    git clone https://github.com/nkhearn/DnD-multi-player-character-app..git
    cd DnD-multi-player-character-app.
    ```

2.  Install the required Python packages:
    ```bash
    pip install Flask Flask-HTTPAuth Werkzeug
    ```

### Directory Structure

Ensure your project directory has the following structure after cloning and setup:

```
your-project-folder/
├── dnd.py
├── app.py
├── viewer_app.py
├── characters/  (This directory will be created automatically on first run if it doesn't exist)
└── templates/
├── indexdm.html
├── character.html
└── viewer.html
└── static/      (This directory will be created automatically on first run if it doesn't exist)
└── ... (any static files like CSS, JS, images go here)
```
The `characters`, `templates`, and `static` directories will be created if they don't exist when the Flask apps are first run.

## Running the Applications

Both Flask applications are designed to run simultaneously on different ports.

1.  **Run the DM Management App (`app.py`):**
    ```bash
    python app.py
    ```
    This app will typically run on port 5000 (the default Flask port) unless configured otherwise. You will see output in your console indicating the development server is running.

2.  **Run the Character Viewer App (`viewer_app.py`):**
    Open a **new terminal window** or tab and run:
    ```bash
    python viewer_app.py
    ```
    This app is configured to run on port 5001.

Keep both terminal windows open as long as you want the web applications to be accessible.

## Usage

### DM Management Interface (`app.py`)

* Access the DM interface in your web browser, usually at `http://127.0.0.1:5000/`.
* You will be prompted for basic HTTP authentication. The default credentials are:
    * **Username:** `dm`
    * **Password:** `password`
    **⚠️ SECURITY WARNING:** As noted in the code, these hardcoded credentials are **highly insecure**. Change the password in `app.py` and consider implementing a more secure authentication method for production use.
* The main page (`/`) will list existing characters.
* Click the "Create New Character" button to generate a new character file.
* Click on a character's name to view and edit their details. Make changes in the form and click "Save Character".
* You can add new conditions or inventory items by filling in the last (empty) row and clicking "Save Character". Empty condition names or inventory items with amount < 1 will be removed on save.

### Character Viewer (`viewer_app.py`)

* Access the viewer interface in your web browser, usually at `http://127.0.0.1:5001/view/<character_name>`.
* Replace `<character_name>` with the full name of a character (e.g., `http://127.0.0.1:5001/view/Zaltar%20the%20Merchant`).
* This page provides a read-only view of the character's current state.
* The corresponding `viewer.html` template is set up to use the `/last_modified` endpoint for polling, the character sheet and will automatically update if the DM saves changes using `app.py`.

Character files are saved in the `characters/` directory as JSON files with a `.chr` extension (e.g., `zaltar_the_merchant.chr`).

## Security Considerations

**The default configuration with hardcoded username and password in `app.py` is NOT secure.**

* **DO NOT** expose the DM Management app (`app.py`) to the public internet with the default credentials.
* Change the `SECRET_KEY` in `app.py` to a unique, random string.
* **Strongly recommended:** Implement a more secure authentication method for `app.py` if used outside a trusted local network, such as:
    * Reading credentials from environment variables or a separate configuration file.
    * Using a database to store hashed passwords.
    * Implementing more robust session management or token-based authentication.

The Viewer app (`viewer_app.py`) has no authentication. Be mindful of what information you are displaying and who can access it if you expose this app beyond your local network.

## Potential Future Enhancements

* More advanced condition effects (affecting stats, saving throws, etc.) in `dnd.py`.
* Calculation of attribute modifiers and proficiency bonus.
* Combat tracking features (initiative, attacks, damage).
* Integration with actual dice rolling.
* Improved UI/UX for the web interfaces, possibly using JavaScript frameworks.
* More robust input validation in the Flask app.
* User accounts and permissions (if needed for a more complex setup).
* A more secure authentication system for the DM app.
* Client-side JavaScript implementation in `viewer.html` to utilize the `/last_modified` endpoint for dynamic updates without full page reloads.
