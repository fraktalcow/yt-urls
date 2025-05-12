from typing import List, Dict
import json
import os

class UserPreferenceManager:
    def __init__(self):
        self.preferences = {
            "categories": {},
            "settings": {
                "duration": {
                    "days": 7,
                    "months": 0
                }
            }
        }
        self.preferences_file = "preference.json"
        self.load_preferences()
    
    def add_category(self, category_name: str) -> bool:
        if category_name not in self.preferences["categories"]:
            self.preferences["categories"][category_name] = []
            return True
        return False
            
    def add_channel(self, channel_name: str, category_name: str) -> bool:
        if category_name not in self.preferences["categories"]:
            self.add_category(category_name)
        
        if channel_name not in self.preferences["categories"][category_name]:
            self.preferences["categories"][category_name].append(channel_name)
            return True
        return False
            
    def remove_channel(self, channel_name: str) -> bool:
        for category in self.preferences["categories"]:
            if channel_name in self.preferences["categories"][category]:
                self.preferences["categories"][category].remove(channel_name)
                return True
        return False
            
    def get_channels(self) -> Dict[str, List[str]]:
        return self.preferences["categories"]
    
    def get_duration(self) -> Dict[str, int]:
        return self.preferences["settings"]["duration"]
    
    def set_duration(self, days: int, months: int) -> None:
        self.preferences["settings"]["duration"]["days"] = days
        self.preferences["settings"]["duration"]["months"] = months
        self.save_preferences()
            
    def import_from_json(self, json_data: Dict):
        self.preferences = json_data
    
    def load_preferences(self):
        try:
            if os.path.exists(self.preferences_file):
                with open(self.preferences_file, 'r') as f:
                    loaded_prefs = json.load(f)
                    # Handle old format migration
                    if "categories" not in loaded_prefs:
                        self.preferences["categories"] = loaded_prefs
                    else:
                        self.preferences = loaded_prefs
            else:
                self.save_preferences()
        except Exception as e:
            print(f"Error loading preferences: {e}")
            self.save_preferences()
    
    def save_preferences(self):
        try:
            with open(self.preferences_file, 'w') as f:
                json.dump(self.preferences, f, indent=4)
        except Exception as e:
            print(f"Error saving preferences: {e}") 