# D&D Character Management System

This project is a web-based application designed to help Dungeon Masters (DMs) manage Dungeons & Dragons (D&D) characters. It also provides a separate interface for players to view their character sheets. The system allows DMs to create, update, and track character statistics, inventory, and conditions, while players can see a real-time view of their character's status.

## Core Features

### Dungeon Master (DM) Interface (`dm_flask.py`)

*   **Character Creation:** Easily create new characters with default stats.
*   **Character Listing:** View all available characters in the system.
*   **Character Editing:** Modify all aspects of a character, including:
    *   Name and basic stats (Max HP, Armour Class, Strength, Dexterity, etc.)
    *   Current Health
    *   Conditions (e.g., Poisoned, Blessed - with numerical effects)
    *   Inventory (items with amounts, values, weights, types)
*   **Password Protection:** The DM interface is protected by basic HTTP authentication.
    *   **Default Credentials:** username: `dm`, password: `password`
    *   **(Important Security Note):** These credentials are hardcoded and should be changed for any real-world use.
*   **QR Code Generation:** For each character, a QR code is generated that links to the player's view of their character sheet, allowing for easy sharing.

### Player Interface (`character_viewer.py`)

*   **Read-Only Character Sheet:** Players can view a clean, read-only version of their character sheet.
*   **Automatic Data Refresh:** The player's character sheet will automatically update if the DM makes changes to the character, ensuring players always see the latest information.

## Project Structure

Here's an overview of the main files and directories in this project:

*   **`dm_flask.py`**: The main Flask application for the Dungeon Master interface. It handles character creation, editing, listing, and provides QR codes for player views.
*   **`character_viewer.py`**: A separate Flask application that provides a public, read-only view of character sheets for players. It includes auto-refresh functionality.
*   **`dnd.py`**: This Python module contains the `dnd_character` class, which encapsulates all the logic for character attributes, health management, conditions, inventory, and saving/loading character data to/from files.
*   **`characters/`**: This directory stores all character data. Each character is saved as a `.chr` file (JSON format) named after the character (e.g., `zaltar_the_merchant.chr`).
*   **`templates/`**: Contains the HTML templates used by both Flask applications to render web pages (e.g., `indexdm.html` for the DM, `viewer.html` for the player).
*   **`static/`**: Holds static files such as CSS stylesheets (`style.css`, `dm.css`) used to style the web pages.
*   **`Readme.md`**: This file, providing information about the project.

## Setup and Installation

Follow these steps to set up and run the D&D Character Management System:

1.  **Prerequisites:**
    *   Python 3 (ensure Python and pip are added to your system's PATH)

2.  **Clone the Repository (if applicable):**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

3.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

4.  **Install Dependencies:**
    Install the necessary Python packages using the provided `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the Applications:**
    You need to run two separate Flask applications:

    *   **For the Dungeon Master (DM) Interface:**
        Open a terminal and run:
        ```bash
        python dm_flask.py
        ```
        This will typically start the DM server on `http://0.0.0.0:5000/`.

    *   **For the Player Character Viewer:**
        Open another terminal and run:
        ```bash
        python character_viewer.py
        ```
        This will typically start the player viewer server on `http://0.0.0.0:5001/`.

    Ensure the `characters/` directory exists in the same location as the scripts, as they will attempt to create it if it's missing, but it's good practice for it to be there.

## Usage

### DM Interface

1.  **Access:** Open your web browser and go to `http://localhost:5000` (or the address shown when you started `dm_flask.py`).
2.  **Login:** You will be prompted for a username and password.
    *   **Default Username:** `dm`
    *   **Default Password:** `password`
3.  **Main Page:** After logging in, you'll see a list of existing characters (if any) and an option to "Create New Character".
4.  **Creating a Character:** Click "Create New Character". A new character with default values will be created and you'll be redirected to its edit page.
5.  **Editing a Character:**
    *   From the main list, click on a character's name to go to their edit page.
    *   Here you can change their name, stats (Max Health, Armour Class, ability scores), current health, add/remove/modify conditions, and manage their inventory.
    *   Click "Add Inventory Item" or "Add Condition" to add new empty slots for items or conditions respectively.
    *   **Important:** Conditions with a value of `0` and inventory items with an amount less than `1` will be removed upon saving.
    *   Changes are saved automatically when you submit the form (e.g., by clicking "Save Character" or when adding/removing items/conditions which triggers a form submission).
6.  **QR Code:** On each character's edit page, a QR code is displayed. This QR code links directly to the player's view for that character (e.g., `http://localhost:5001/view/Character%20Name`). You can share this with your players.

### Player Interface

1.  **Access:** Players can access their character sheets by:
    *   Scanning the QR code provided by the DM.
    *   Directly navigating to the URL, typically `http://localhost:5001/view/<CharacterName>` (e.g., `http://localhost:5001/view/Zaltar%20the%20Merchant`). The character name in the URL should be URL-encoded if it contains spaces.
2.  **Viewing:** The character sheet is displayed in a read-only format.
3.  **Automatic Updates:** If the DM makes changes to the character while the player has the sheet open, the sheet should automatically refresh to display the latest information.

## Future Enhancements

This project provides a solid foundation for D&D character management. Here are some potential ideas for future development:

*   **More Robust Authentication:** Replace the hardcoded basic authentication with a more secure system (e.g., Flask-Login, OAuth, database-backed user accounts).
*   **Database Integration:** Instead of storing characters in individual JSON files, use a database (e.g., SQLite, PostgreSQL, MongoDB) for more efficient data management, querying, and scalability.
*   **User Accounts for DMs:** Allow multiple DMs to create accounts and manage their own sets of characters.
*   **Campaign Management:** Add features to group characters into campaigns.
*   **Dice Rolling Functionality:** Integrate a dice roller into the application.
*   **Spells and Abilities:** Add dedicated sections for managing character spells, special abilities, and class features.
*   **Notes Section:** Allow DMs and/or players to add notes to character sheets.
*   **Improved UI/UX:** Enhance the user interface for better usability and visual appeal.
*   **API for Third-Party Integrations:** Develop an API to allow other tools or services to interact with the character data.
*   **Export/Import Characters:** Allow characters to be exported in different formats (e.g., PDF, plain text) or imported from other systems.

## License

This project is currently not licensed.

It is recommended to add an open-source license to define how others can use, modify, and distribute the code. A common choice for projects like this is the [MIT License](https://opensource.org/licenses/MIT).

To add a license:
1.  Create a file named `LICENSE` in the root of the project.
2.  Copy the text of your chosen license (e.g., the MIT License template) into this file.
3.  Update this section in the `Readme.md` to reflect the chosen license (e.g., "This project is licensed under the MIT License - see the LICENSE file for details.").
