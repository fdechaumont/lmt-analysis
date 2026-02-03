"""
@creation: 12-03-2025
@author: fab
@modification: 15-02-2026
@modifier: xmousset
"""

import json
from pathlib import Path
from typing import Any, Dict, List


class ParameterSaver(object):
    """This class is dedicated to save and load parameters with json files."""

    def __init__(self, save_folder: Path):
        self.save_folder = save_folder
        self.reset()

    def set_parameters(self, data: Dict[str, Any]):
        """Set multiple parameters at once."""
        self.data = data

    def reset(self):
        """Reset all saved parameters."""
        self.data: Dict[str, Any] = {}

    def get_parameters(self):
        """Get all saved parameters."""
        return self.data

    def get_value(self, key: str):
        """Get a single parameter by key."""
        return self.data.get(key)

    def get_values(self, keys: List[str]) -> List[Any]:
        """Get multiple parameters by keys."""
        return [self.data.get(key) for key in keys]

    def set_value(self, key: str, value: Any):
        """Set a single parameter by key."""
        self.data[key] = value

    def set_values(self, data: Dict[str, Any]):
        """Set multiple parameters with dict."""
        self.data.update(data)

    def save(self, name: str = "saved_parameters"):
        """Save current config as the default config."""
        file_path = self.save_folder / f"{name}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
            print(f"Save data in: {file_path}")
        except Exception as e:
            print(f"Failed to save json: {e}")

    def load(self, name: str = "saved_parameters"):
        """Load config from the default config file."""
        file_path = self.save_folder / f"{name}.json"
        if file_path.is_file():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                print(f"Load data from: {file_path}")
                print(f"Loaded data: {self.data}")
            except Exception as e:
                print(f"Failed to load json: {e}")
        else:
            print(f"No default json found at {file_path}")
