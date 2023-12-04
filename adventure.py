import json
import sys

# Abbreviations for directions and commands
abbreviations = {
    # ... [unchanged content] ...
    "g": "get",
    "g": "go",
    "i": "items",
    "i": "inventory"
}

direction_abbreviations = {
    # ... [unchanged content] ...
    "n": "north",
    "e": "east",
    "s": "south",
    "w": "west",
    "ne": "northeast",
    "nw": "northwest",
    "se": "southeast",
    "sw": "southwest",
    
}

class AdventureGame:
    def __init__(self, map_file):
        self.map_file = map_file
        self.load_map()
        self.current_location = 0
        self.player_inventory = []
        self.game_running = True

    def load_map(self):
        with open(self.map_file, 'r') as file:
            self.game_map = json.load(file)

    def start_game(self):
        self.look()
        while self.game_running:
            self.prompt_command()

    def prompt_command(self):
        try:
            command = input("What would you like to do? ").strip().lower()
            self.process_command(command)
        except EOFError:
            print("\nUse 'quit' to exit.")

    def process_command(self, command):
        command_parts = command.split()
        base_command = self.get_base_command(command_parts[0])

        if base_command in ["north", "east", "south", "west", "northeast", "northwest", "southeast", "southwest"]:
            self.move_player(base_command)
        elif base_command == "go":
            self.handle_go_command(command_parts)
        else:
            self.handle_other_commands(base_command, command_parts)

    def get_base_command(self, command):
        if command in abbreviations:
            return abbreviations[command]
        if command in direction_abbreviations:
            return "go"
        return command

    def handle_go_command(self, command_parts):
        if len(command_parts) > 1:
            direction = direction_abbreviations.get(command_parts[1], command_parts[1])
            self.move_player(direction)
        else:
            print("Sorry, you need to 'go' somewhere.")

    def handle_other_commands(self, base_command, command_parts):
        # Map command strings to their corresponding methods
        command_methods = {
            "look": self.look,
            "get": self.handle_get_command,
            "drop": self.handle_drop_command,
            "inventory": self.show_inventory,
            "items": self.show_items,
            "help": self.show_help,
            "exits": self.show_exits,
            "quit": self.quit_game
        }

        if base_command in command_methods and len(command_parts)>1:
            command_methods[base_command](command_parts)
        elif base_command == "get":
            print("Sorry, you need to 'get' something.")
        elif base_command in command_methods:
            command_methods[base_command]()
        else:
            print("Invalid command. Try 'help' for a list of valid commands.")
    
    def move_player(self, direction):
        current_location = self.game_map[self.current_location]
        if direction in current_location["exits"]:
            next_location_index = current_location["exits"][direction]
            next_location = self.game_map[next_location_index]
            
            # Check if the next location is locked and requires a key
            if next_location.get("locked", False) and "key" in next_location:
                required_item = next_location["key"]
                
                # Check if the player has the required key to unlock the door
                if required_item in self.player_inventory:
                    print(f"You go {direction}.")
                    print(f"Using {required_item} to unlock the door.")
                    self.current_location = next_location_index
                    self.look()
                    self.check_condition()
                else:
                    print(f"You go {direction}.")
                    print("The door is locked. You need something to unlock it.")
            else:
                self.current_location = next_location_index
                print(f"You go {direction}.")
                print()
                self.look()
                self.check_condition()
        else:
            print(f"There's no way to go {direction}.")

            
    def check_condition(self):
        location = self.game_map[self.current_location]
        conditions = location.get("conditions", {})
        
        # Check winning condition
        win_condition = conditions.get("win")
        if win_condition and win_condition["item"] in self.player_inventory:
                print(win_condition["message"])
                self.game_running = False 
        elif conditions.get("lose"):
            lose_condition = conditions.get("lose")
            print(lose_condition["message"])
            self.game_running = False 

    def look(self):
        location = self.game_map[self.current_location]
        print(f"> {location['name']}\n")
        print(f"{location['desc']}\n")
        if "items" in location and len(location["items"])>0:
            print("Items: " + " ".join(location["items"]))
            print()
        if "exits" in location:
            print("Exits: " + " ".join(location["exits"].keys()))
        print()

    def handle_get_command(self, command_parts):
        if len(command_parts) > 1:
            item_abbr = " ".join(command_parts[1:])
            self.get_item_by_abbr(item_abbr)
        else:
            print("Sorry, you need to 'get' something.")

    def get_item_by_abbr(self, item_abbr):
        location = self.game_map[self.current_location]
        matching_items = [item for item in location.get("items", []) if item.lower().startswith(item_abbr.lower())]
        if matching_items:
            self.pick_up_item(matching_items[0])
        else:
            print(f"There is no {item_abbr} anywhere.")

    def pick_up_item(self, item_name):
        location = self.game_map[self.current_location]
        if item_name in location["items"]:
            location["items"].remove(item_name)
            self.player_inventory.append(item_name)
            print(f"You pick up the {item_name}.")
        else:
            print(f"There is no {item_name} anywhere.")

    def handle_drop_command(self, command_parts):
        if len(command_parts) > 1:
            item_name = " ".join(command_parts[1:])
            self.drop_item(item_name)
        else:
            print("You must specify an item to drop.")

    def drop_item(self, item_name):
        if item_name in self.player_inventory:
            self.player_inventory.remove(item_name)
            self.game_map[self.current_location].setdefault("items", []).append(item_name)
            print(f"You dropped the {item_name}.")
        else:
            print(f"You don't have {item_name}.")

    def show_inventory(self):
        if self.player_inventory:
            print("Inventory:")
            for i in self.player_inventory:
                print(" ",i)
        else:
            print("You're not carrying anything.")

    def show_items(self):
        location = self.game_map[self.current_location]
        if "items" in location and location["items"]:
            print("Items in this location: " + " ".join(location["items"]))
        else:
            print("There are no items here.")

    def show_exits(self):
        location = self.game_map[self.current_location]
        if "exits" in location:
            print("Available exits: " + " ".join(location["exits"].keys()))
    
    def show_help(self):
        print("Available commands:")
        print("  go [direction] - Move in the specified direction (north, south, east, west).")
        print("  get [item] - Pick up an item from the current location.")
        print("  drop [item] - Drop an item from your inventory into the current location.")
        print("  inventory - Show the items you are carrying.")
        print("  look - Describe the current location.")
        print("  items - List all items in the current location.")
        print("  exits - Show all available exits from the current location.")
        print("  help - Display this help message.")
        print("  quit - Exit the game.")
    
    def quit_game(self):
        print("Goodbye!")
        self.game_running = False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 adventure.py [map_file]")
        return
    map_file = sys.argv[1]
    game = AdventureGame(map_file)
    game.start_game()

if __name__ == "__main__":
    main()

