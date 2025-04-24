from typing import List, Dict
import json

class UserPreferenceManager:
    def __init__(self):
        self.preferences: Dict[str, List[str]] = {}
    
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
                
    @classmethod
    def initialize_with_defaults(cls) -> 'UserPreferenceManager':
        manager = cls()
        default_preferences = {
            "Mathematics": ["3Blue1Brown", "Numberphile", "patrickjmt"],
            "Programming": ["realpython", "ThePrimeTimeagen", "MachineLearningStreetTalk"],
            "Philosophy": ["ThePartiallyExaminedLife"],
            "Comedy": ["xQcOW", "standupots"]
        }
        manager.import_from_json(default_preferences)
        return manager 