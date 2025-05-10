from typing import List, Dict
import json
import os

class UserPreferenceManager:
    def __init__(self):
        self.preferences: Dict[str, List[str]] = {}
        self.preferences_file = "preference.json"
        self.load_preferences()
    
    def add_category(self, category_name: str) -> bool:
        if category_name not in self.preferences:
            self.preferences[category_name] = []
            return True
        return False
            
    def add_channel(self, channel_name: str, category_name: str) -> bool:
        if category_name not in self.preferences:
            self.add_category(category_name)
        
        if channel_name not in self.preferences[category_name]:
            self.preferences[category_name].append(channel_name)
            return True
        return False
            
    def remove_channel(self, channel_name: str) -> bool:
        for category in self.preferences:
            if channel_name in self.preferences[category]:
                self.preferences[category].remove(channel_name)
                return True
        return False
            
    def get_channels(self) -> Dict[str, List[str]]:
        return self.preferences
            
    def import_from_json(self, json_data: Dict[str, List[str]]):
        self.preferences = json_data
    
    def load_preferences(self):
        try:
            if os.path.exists(self.preferences_file):
                with open(self.preferences_file, 'r') as f:
                    self.preferences = json.load(f)
            else:
                # If file doesn't exist, create empty preferences
                self.preferences = {}
                self.save_preferences()
        except Exception as e:
            print(f"Error loading preferences: {e}")
            self.preferences = {}
            self.save_preferences()
    
    def save_preferences(self):
        try:
            with open(self.preferences_file, 'w') as f:
                json.dump(self.preferences, f, indent=4)
        except Exception as e:
            print(f"Error saving preferences: {e}") 