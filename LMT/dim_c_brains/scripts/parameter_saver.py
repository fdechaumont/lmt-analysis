"""
@creation: 12-03-2025
@author: fab
@modification: 15-02-2026
@modifier: xmousset
"""

import json
from pathlib import Path
from tkinter import filedialog
from typing import Any, Dict, List


class ParameterSaver(object):
    """This class is dedicated to save and load parameters with json files."""

    def __init__(self):
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

    def save(self, file_path: Path):
        """Save data to the given path. If the path is a directory, it will
        save the file 'saved_parameters.json' inside it."""
        if file_path.is_dir():
            save_path = file_path / "saved_parameters.json"
        else:
            save_path = file_path

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
            print(f"Save data in: {save_path}")
        except Exception as e:
            print(f"Failed to save json: {e}")

    def load(self, file_path: Path):
        """Load data from the given path. If the path is a directory, it will
        look for 'saved_parameters.json' inside it."""
        if file_path.is_dir():
            load_path = file_path / "saved_parameters.json"
        else:
            load_path = file_path

        if load_path.is_file():
            try:
                with open(load_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                print(f"Load data from: {load_path}")
                print(f"Loaded data: {self.data}")
            except Exception as e:
                print(f"Failed to load json: {e}")
        else:
            print(f"No default json found at {load_path}")

    def ask_save_name(self, open_dir: Path | None = None) -> Path:
        file_path = Path(
            filedialog.asksaveasfilename(
                title="Select JSON file",
                initialdir=str(open_dir) if open_dir is not None else None,
                filetypes=[("JSON Files", "*.json")],
            )
        )
        return file_path

    def ask_load_name(self, open_dir: Path | None = None) -> Path:
        """Open a file dialog to select a json file to load. It will start in
        the given directory."""

        file_path = Path(
            filedialog.askopenfilename(
                title="Select JSON file",
                initialdir=str(open_dir) if open_dir is not None else None,
                filetypes=[("JSON Files", "*.json")],
            )
        )
        return file_path
