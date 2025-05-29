import sqlite3

# Define the name of the database file
DB_NAME = "dnd_characters.db"

def create_tables():
    """Creates the necessary tables in the SQLite database if they don't already exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create characters table
    # Stores information about each character
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS characters (
            name TEXT PRIMARY KEY,         -- Character's unique name
            max_health INTEGER,            -- Maximum health points
            current_health INTEGER,        -- Current health points
            armour_class INTEGER,          -- Armour Class (AC)
            strength INTEGER,              -- Strength score
            dexterity INTEGER,             -- Dexterity score
            constitution INTEGER,          -- Constitution score
            intelligence INTEGER,          -- Intelligence score
            wisdom INTEGER,                -- Wisdom score
            charisma INTEGER               -- Charisma score
        )
    """)

    # Create conditions table
    # Stores temporary or persistent conditions affecting characters
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conditions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique ID for the condition entry
            character_name TEXT,                 -- Name of the character affected
            name TEXT,                           -- Name of the condition (e.g., "Poisoned", "Advantage on Strength Saves")
            value INTEGER,                       -- Numerical value associated with the condition, if any (e.g., levels of exhaustion)
            attribute TEXT,                      -- Specific attribute affected, if any (e.g., "Strength", "Saving Throws")
            FOREIGN KEY (character_name) REFERENCES characters(name) -- Links to the characters table
        )
    """)

    # Create inventory table
    # Stores items held by characters
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique ID for the inventory item
            character_name TEXT,                 -- Name of the character who owns the item
            name TEXT,                           -- Name of the item (e.g., "Longsword", "Potion of Healing")
            amount INTEGER,                      -- Quantity of the item
            value REAL,                          -- Value of the item (e.g., for potions or magical effects, could be dice like '1d4+1')
            weight REAL,                         -- Weight of a single item
            gold_value REAL,                     -- Value of the item in gold pieces
            type TEXT,                           -- Type of item (e.g., "Weapon", "Armor", "Potion", "Scroll")
            FOREIGN KEY (character_name) REFERENCES characters(name) -- Links to the characters table
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database '{DB_NAME}' and tables created successfully.")

if __name__ == "__main__":
    create_tables()
