import json
import os

class dnd_character:
    """
    Represents a Dungeons & Dragons character with standard attributes,
    inventory, and methods for managing health, conditions, saving/loading,
    and logging messages.
    """

    def __init__(self, name="Unnamed Character", max_health=100, armour_class=10,
                 strength=10, dexterity=10, constitution=10,
                 intelligence=10, wisdom=10, charisma=10):
        """
        Initializes a new D&D character.

        Args:
            name (str): The character's name.
            max_health (int): The maximum health points of the character.
            armour_class (int): The character's armour class.
            strength (int): The character's Strength score.
            dexterity (int): The character's Dexterity score.
            constitution (int): The character's Constitution score.
            intelligence (int): The character's Intelligence score.
            wisdom (int): The character's Wisdom score.
            charisma (int): The character's Charisma score.
        """
        self.name = name
        self.max_health = max_health
        self._current_health = max_health  # Use a protected attribute for current health
        self.armour_class = armour_class
        self.strength = strength
        self.dexterity = dexterity
        self.constitution = constitution
        self.intelligence = intelligence
        self.wisdom = wisdom
        self.charisma = charisma
        # Conditions stored as a list of dictionaries:
        # [{'name': 'Poisoned', 'value': -2, 'attribute': 'strength'}]
        self._conditions = []
        # Inventory stored as a list of dictionaries:
        # [{'name': 'Healing Potion', 'amount': 2, 'value': 50, 'weight': 0.5, 'gold_value': 10, 'type': 'Consumable'}]
        self._inventory = []
        self._messages = [] # List to store messages
        #return self

    def health(self, adjustment=None):
        """
        Manages the character's current health.

        If adjustment is None, returns the current health.
        If adjustment is a number, adjusts the current health by that amount.
        Health cannot exceed max_health or drop below 0.

        Args:
            adjustment (int, optional): The amount to adjust health by.
                                        Defaults to None.

        Returns:
            tuple: A tuple containing the character's current health and a list of messages.
        """
        self._messages = [] # Clear messages for this call

        if adjustment is None:
            return self._current_health, self._messages
        else:
            try:
                # Ensure adjustment is treated as an integer
                adjustment = int(adjustment)
                self._current_health += adjustment
                # Cap health at max_health
                if self._current_health > self.max_health:
                    self._current_health = self.max_health
                    self._messages.append(f"Health capped at max health: {self.max_health}")
                # Prevent health from dropping below 0
                if self._current_health < 0:
                    self._current_health = 0
                    self._messages.append("Health cannot drop below 0.")

                self._messages.append(f"Health adjusted by {adjustment}. Current health: {self._current_health}")
                return self._current_health, self._messages
            except (ValueError, TypeError):
                self._messages.append("Invalid health adjustment. Please provide a number.")
                return self._current_health, self._messages # Return current health and error message

    def condition(self, name=None, value=None, attribute=None):
        """
        Manages the character's conditions.

        If name and value are None, returns the list of current conditions.
        If name and value are provided:
            If value is 0, removes the condition with the given name.
            If value is not 0, adds or updates the condition with the given
            name, value, and optional attribute.

        Args:
            name (str, optional): The name of the condition. Defaults to None.
            value (int, optional): The numeric value of the condition. Defaults to None.
                                   Use 0 to remove a condition.
            attribute (str, optional): The character attribute the condition affects.
                                       Defaults to None.

        Returns:
            tuple: A tuple containing the updated list of conditions and a list of messages.
        """
        self._messages = [] # Clear messages for this call

        if name is None and value is None:
            return self._conditions, self._messages
        elif name is not None and value is not None:
            # Check if the condition already exists
            existing_condition_index = -1
            for i, cond in enumerate(self._conditions):
                if cond['name'].lower() == name.lower(): # Case-insensitive check
                    existing_condition_index = i
                    break

            if value == 0:
                # Remove the condition if value is 0
                if existing_condition_index != -1:
                    del self._conditions[existing_condition_index]
                    self._messages.append(f"Condition '{name}' removed.")
                else:
                    self._messages.append(f"Condition '{name}' not found.")
            else:
                # Add or update the condition
                new_condition = {'name': name, 'value': value, 'attribute': attribute}
                if existing_condition_index != -1:
                    # Update existing condition
                    self._conditions[existing_condition_index] = new_condition
                    self._messages.append(f"Condition '{name}' updated.")
                else:
                    # Add new condition
                    self._conditions.append(new_condition)
                    self._messages.append(f"Condition '{name}' added.")

            return self._conditions, self._messages
        else:
            self._messages.append("To add/update/remove a condition, both 'name' and 'value' must be provided.")
            return self._conditions, self._messages

    def run_conditions(self):
        """
        Processes all current conditions and applies their effects,
        specifically those that affect 'health'.

        Applies the numeric value of any condition with attribute='health'
        to the character's current health.

        Returns:
            tuple: A tuple containing the total sum of health adjustments
                   made by conditions and a list of messages.
        """
        self._messages = [] # Clear messages for this call
        total_adjustment = 0
        # Iterate over a copy of the list in case conditions are removed later
        for condition in list(self._conditions):
            if condition.get('attribute', '').lower() == 'health': # Case-insensitive check for attribute
                adjustment = condition.get('value', 0) # Get value, default to 0 if not found
                if adjustment != 0:
                    self._messages.append(f"Applying condition '{condition['name']}': adjusting health by {adjustment}")
                    # Use the health method to apply the adjustment; it will add its own messages
                    health_result, health_messages = self.health(adjustment)
                    self._messages.extend(health_messages) # Add messages from the health call
                    total_adjustment += adjustment

        self._messages.append(f"Finished running conditions. Total health adjustment: {total_adjustment}")
        return total_adjustment, self._messages

    def add_item(self, name, amount, value, weight, gold_value, item_type):
        """
        Adds an item to the inventory or updates the amount if the item exists.

        Args:
            name (str): The name of the item.
            amount (int): The quantity of the item. Must be a positive integer.
            value (float): The value of a single item (e.g., for selling).
            weight (float): The weight of a single item.
            gold_value (float): The value of a single item in British Pounds (£).
            item_type (str): The type of item (e.g., 'Weapon', 'Armor', 'Consumable').

        Returns:
            tuple: A tuple containing the updated inventory list and a list of messages.
        """
        self._messages = [] # Clear messages for this call

        if not isinstance(amount, int) or amount <= 0:
            self._messages.append("Amount must be a positive integer.")
            return self._inventory, self._messages
        if not all(isinstance(val, (int, float)) for val in [value, weight, gold_value]):
             self._messages.append("Value, weight, and gold value must be numbers.")
             return self._inventory, self._messages
        if not isinstance(name, str) or not name.strip():
             self._messages.append("Item name cannot be empty.")
             return self._inventory, self._messages
        if not isinstance(item_type, str) or not item_type.strip():
             self._messages.append("Item type cannot be empty.")
             return self._inventory, self._messages


        # Check if item already exists by name (case-insensitive)
        existing_item_index = -1
        for i, item in enumerate(self._inventory):
            if item['name'].lower() == name.lower():
                existing_item_index = i
                break

        if existing_item_index != -1:
            # Item exists, update amount
            self._inventory[existing_item_index]['amount'] += amount
            self._messages.append(f"Added {amount} x '{name}'. Total amount: {self._inventory[existing_item_index]['amount']}")
        else:
            # Item does not exist, add new item
            new_item = {
                'name': name,
                'amount': amount,
                'value': float(value), # Ensure float
                'weight': float(weight), # Ensure float
                'gold_value': float(gold_value), # Ensure float
                'type': item_type
            }
            self._inventory.append(new_item)
            self._messages.append(f"Added new item: '{name}' ({amount})")

        return self._inventory, self._messages

    def adjust_item_amount(self, name, adjustment):
        """
        Adjusts the amount of an item in the inventory.
        If the amount reaches 0 or less, the item is removed.

        Args:
            name (str): The name of the item to adjust.
            adjustment (int): The amount to add (positive) or remove (negative).

        Returns:
            tuple: A tuple containing the updated inventory list and a list of messages.
        """
        self._messages = [] # Clear messages for this call

        if not isinstance(adjustment, int):
            self._messages.append("Adjustment amount must be an integer.")
            return self._inventory, self._messages
        if not isinstance(name, str) or not name.strip():
             self._messages.append("Item name cannot be empty.")
             return self._inventory, self._messages


        # Find the item by name (case-insensitive)
        item_index = -1
        for i, item in enumerate(self._inventory):
            if item['name'].lower() == name.lower():
                item_index = i
                break

        if item_index != -1:
            # Item found, adjust amount
            self._inventory[item_index]['amount'] += adjustment
            item_name = self._inventory[item_index]['name'] # Use original name for message

            if self._inventory[item_index]['amount'] <= 0:
                # Amount is zero or less, remove item
                del self._inventory[item_index]
                self._messages.append(f"Removed '{item_name}' as amount reached 0 or less.")
            else:
                # Amount is still positive
                self._messages.append(f"Adjusted amount for '{item_name}' by {adjustment}. New amount: {self._inventory[item_index]['amount']}")
        else:
            # Item not found
            self._messages.append(f"Item '{name}' not found in inventory.")

        return self._inventory, self._messages

    def list_inventory(self, name=None, item_type=None):
        """
        Returns a list of inventory items, optionally filtered by name or type.

        Args:
            name (str, optional): Filter by item name (case-insensitive). Defaults to None.
            item_type (str, optional): Filter by item type (case-insensitive). Defaults to None.

        Returns:
            tuple: A tuple containing the filtered list of items and a list of messages.
        """
        self._messages = [] # Clear messages for this call
        filtered_inventory = self._inventory

        if name is not None and isinstance(name, str) and name.strip():
            name_lower = name.lower()
            filtered_inventory = [item for item in filtered_inventory if item['name'].lower() == name_lower]
            self._messages.append(f"Filtered inventory by name: '{name}'")

        if item_type is not None and isinstance(item_type, str) and item_type.strip():
            type_lower = item_type.lower()
            filtered_inventory = [item for item in filtered_inventory if item['type'].lower() == type_lower]
            self._messages.append(f"Filtered inventory by type: '{item_type}'")

        if name is None and item_type is None:
            self._messages.append("Listing all inventory items.")
        elif not filtered_inventory:
             if name and item_type:
                 self._messages.append(f"No items found matching name '{name}' and type '{item_type}'.")
             elif name:
                 self._messages.append(f"No items found matching name '{name}'.")
             elif item_type:
                 self._messages.append(f"No items found matching type '{item_type}'.")


        return filtered_inventory, self._messages


    def save(self, directory_path="character_saves"):
        """
        Saves the character's current state (attributes, conditions, inventory)
        to a JSON file in the specified directory.

        The filename will be "{character_name}.chr".

        Args:
            directory_path (str): The path to the directory where the file
                                  will be saved. Defaults to "character_saves".

        Returns:
            tuple: A tuple containing a boolean indicating success (True) or failure (False)
                   and a list of messages.
        """
        self._messages = [] # Clear messages for this call

        # Ensure the directory exists
        try:
            os.makedirs(directory_path, exist_ok=True)
            self._messages.append(f"Ensured directory '{directory_path}' exists.")
        except OSError as e:
            self._messages.append(f"Error creating directory '{directory_path}': {e}")
            return False, self._messages


        # Construct the full file path
        filename = f"{self.name.replace(' ', '_').lower()}.chr" # Create a safe filename
        file_path = os.path.join(directory_path, filename)

        # Prepare the data to be saved
        character_data = {
            "name": self.name,
            "max_health": self.max_health,
            "_current_health": self._current_health,
            "armour_class": self.armour_class,
            "strength": self.strength,
            "dexterity": self.dexterity,
            "constitution": self.constitution,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "charisma": self.charisma,
            "_conditions": self._conditions,
            "_inventory": self._inventory # Include inventory
        }

        try:
            with open(file_path, 'w') as f:
                json.dump(character_data, f, indent=4) # Use indent for readability
            self._messages.append(f"Character '{self.name}' saved successfully to '{file_path}'")
            return True, self._messages
        except IOError as e:
            self._messages.append(f"Error saving character '{self.name}': {e}")
            return False, self._messages
        except Exception as e:
            self._messages.append(f"An unexpected error occurred while saving '{self.name}': {e}")
            return False, self._messages

    def load(self, directory_path="characters"):
        """
        Loads the character's state from a JSON file in the specified directory.

        The filename is expected to be "{character_name}.chr".

        Args:
            directory_path (str): The path to the directory where the file
                                  is located. Defaults to "character_saves".

        Returns:
            tuple: A tuple containing a boolean indicating success (True) or failure (False)
                   and a list of messages.
        """
        self._messages = [] # Clear messages for this call

        # Construct the full file path
        filename = f"{self.name.replace(' ', '_').lower()}.chr" # Match filename format
        file_path = os.path.join(directory_path, filename)

        if not os.path.exists(file_path):
            self._messages.append(f"Save file not found for character '{self.name}' at '{file_path}'")
            return False, self._messages

        try:
            with open(file_path, 'r') as f:
                character_data = json.load(f)

            # Load the data into the current character object
            self.name = character_data.get("name", self.name) # Use .get() with default to be safe
            self.max_health = character_data.get("max_health", self.max_health)
            self._current_health = character_data.get("_current_health", self._current_health)
            self.armour_class = character_data.get("armour_class", self.armour_class)
            self.strength = character_data.get("strength", self.strength)
            self.dexterity = character_data.get("dexterity", self.dexterity)
            self.constitution = character_data.get("constitution", self.constitution)
            self.intelligence = character_data.get("intelligence", self.intelligence)
            self.wisdom = character_data.get("wisdom", self.wisdom)
            self.charisma = character_data.get("charisma", self.charisma)
            self._conditions = character_data.get("_conditions", []) # Default to empty list if not found
            self._inventory = character_data.get("_inventory", []) # Default to empty list if not found

            self._messages.append(f"Character '{self.name}' loaded successfully from '{file_path}'")
            return True, self._messages

        except json.JSONDecodeError:
            self._messages.append(f"Error decoding JSON from file '{file_path}'. File might be corrupted.")
            return False, self._messages
        except FileNotFoundError:
             # This case should be caught by os.path.exists, but included for robustness
            self._messages.append(f"Save file not found for character '{self.name}' at '{file_path}'")
            return False, self._messages
        except Exception as e:
            self._messages.append(f"An unexpected error occurred while loading '{self.name}': {e}")
            return False, self._messages


# Helper function to display results and messages
def display_result_and_messages(result, messages):
    """Helper function to print the result and associated messages."""
    print(f"Result:")
    # Handle different types of results for better display
    if isinstance(result, list):
        if not result:
            print("  (Empty List)")
        else:
            for item in result:
                print(f"  {item}")
    else:
        print(f"  {result}")

    if messages:
        print("Messages:")
        for msg in messages:
            print(f"- {msg}")
    print("-" * 20)


# Example Usage:
if __name__ == "__main__":
    # --- Create a character and add items ---
    print("--- Creating Character and Adding Items ---")
    my_character = dnd_character(name="Zaltar the Merchant", max_health=70)
    print(my_character.name)

    inv_result, inv_messages = my_character.add_item("Healing Potion", 3, 50.0, 0.5, 10.0, "Consumable")
    display_result_and_messages(inv_result, inv_messages)

    inv_result, inv_messages = my_character.add_item("Iron Sword", 1, 100.0, 10.0, 20.0, "Weapon")
    display_result_and_messages(inv_result, inv_messages)

    inv_result, inv_messages = my_character.add_item("Rope", 1, 10.0, 5.0, 2.0, "Utility")
    display_result_and_messages(inv_result, inv_messages)

    inv_result, inv_messages = my_character.add_item("Healing Potion", 2, 50.0, 0.5, 10.0, "Consumable") # Add more potions
    display_result_and_messages(inv_result, inv_messages)

    inv_result, inv_messages = my_character.add_item("Leather Armor", 1, 50.0, 15.0, 10.0, "Armor")
    display_result_and_messages(inv_result, inv_messages)

    print("\n" + "="*30 + "\n") # Separator

    # --- List Inventory ---
    print("--- Listing Inventory ---")
    all_items, list_messages = my_character.list_inventory()
    display_result_and_messages(all_items, list_messages)

    print("\n" + "="*30 + "\n") # Separator

    print("--- Listing Consumables ---")
    consumables, list_messages = my_character.list_inventory(item_type="Consumable")
    display_result_and_messages(consumables, list_messages)

    print("\n" + "="*30 + "\n") # Separator

    print("--- Listing Iron Sword ---")
    swords, list_messages = my_character.list_inventory(name="Iron Sword")
    display_result_and_messages(swords, list_messages)

    print("\n" + "="*30 + "\n") # Separator

    print("--- Listing non-existent item ---")
    non_existent, list_messages = my_character.list_inventory(name="Magic Wand")
    display_result_and_messages(non_existent, list_messages)

    print("\n" + "="*30 + "\n") # Separator

    # --- Adjust Item Amount ---
    print("--- Adjusting Item Amount ---")
    adj_result, adj_messages = my_character.adjust_item_amount("Healing Potion", -1) # Use one potion
    display_result_and_messages(adj_result, adj_messages)

    adj_result, adj_messages = my_character.adjust_item_amount("Healing Potion", -5) # Use more than available (should remove)
    display_result_and_messages(adj_result, adj_messages)

    adj_result, adj_messages = my_character.adjust_item_amount("Iron Sword", 1) # Find a new sword
    display_result_and_messages(adj_result, adj_messages)

    adj_result, adj_messages = my_character.adjust_item_amount("NonExistentItem", -1) # Try adjusting non-existent
    display_result_and_messages(adj_result, adj_messages)

    print("\n" + "="*30 + "\n") # Separator

    print("--- Listing Inventory After Adjustments ---")
    all_items_after_adj, list_messages_after_adj = my_character.list_inventory()
    display_result_and_messages(all_items_after_adj, list_messages_after_adj)
    my_character.condition("bleeding",-1,"health")

    print("\n" + "="*30 + "\n") # Separator

    # --- Demonstrate Saving with Inventory ---
    print("--- Demonstrating Save with Inventory ---")
    save_directory = "characters"
    save_success, save_messages = my_character.save(save_directory)
    display_result_and_messages(f"Save Successful: {save_success}", save_messages)

    print("\n" + "="*30 + "\n") # Separator

    # --- Demonstrate Loading with Inventory ---
    print("--- Demonstrating Load with Inventory ---")
    loaded_character = dnd_character(name="Zaltar the Merchant") # Name must match for loading

    print(f"New character object '{loaded_character.name}' before loading:")
    initial_inv, _ = loaded_character.list_inventory()
    print(f"  Inventory: {initial_inv}") # Should be empty
    print("-" * 20)

    load_success, load_messages = loaded_character.load(save_directory)
    display_result_and_messages(f"Load Successful: {load_success}", load_messages)

    if load_success:
        print(f"Character '{loaded_character.name}' after loading:")
        loaded_inv, _ = loaded_character.list_inventory()
        display_result_and_messages(loaded_inv, ["Loaded Inventory:"]) # Use a custom message for clarity

    print("\n" + "="*30 + "\n") # Separator

    # Clean up the created save file and directory (optional)
    # import shutil
    # try:
    #     shutil.rmtree(save_directory)
    #     print(f"Cleaned up directory '{save_directory}'")
    # except OSError as e:
    #     print(f"Error cleaning up directory {save_directory}: {e}")


