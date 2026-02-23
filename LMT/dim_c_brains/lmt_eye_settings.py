"""
@author: xmousset
"""

from typing import Any
from pathlib import Path

import pandas as pd

from dim_c_brains.scripts.parameter_saver import ParameterSaver

from lmtanalysis.Animal import AnimalType
from lmtanalysis.Measure import oneMinute, oneDay


class LMTEYESettings:
    """Manage parameters for LMT analysis.

    Parameters
    ----------
    animal_type : AnimalType, optional
        Type of animal for event processing. Defaults to AnimalType.MOUSE.
    events : set of str, optional
        Set of event names to analyze. By default, no event analysis is
        performed (empty set).
    filter_flickering : bool, optional
        Whether to filter the 'Flickering' event for animal activity.
        Defaults to False.
    filter_stop : bool, optional
        Whether to filter the 'Stop' event for animal activity.
        Defaults to False.
    fps : int, optional
        Frame rate of the recording in *frames per second*. Defaults to 30.
    night_begin : int, optional
        Hour when the night begins (0-23). Defaults to 20 (8 *p.m.*).
    night_duration : int, optional
        Duration of the night in hours. Defaults to 12 (12 hours so from
        8 *p.m.* to 8 *a.m.* for example).
    output_folder : Path or str or None, optional
        Folder to save the output reports. By default, prompts user to
        select folder ('manual selection').
    processing_limits : tuple of int or pd.Timestamp or None, optional
        Start and end of the processing period. Each can be an integer frame
        number or a timestamp string. Defaults to (None, None).
        *(timestamp string example: "2026-01-01 00:00:00")*
    processing_window : int, optional
        Load a maximum of 'processing_window' *frames* simultaneously. If the
        data is bigger than this window, the computation will be splitted into
        chunks of 'processing_window' size. Defaults to *2 592 000 frames (=1
        day)*.
    rebuild_events : bool, optional
        Whether to rebuild all the events to analyse in the database before
        analysis. If False, only missing events will be rebuilt. Defaults to
        False.
    time_window : int, optional
        Time window for data binning in *frames*. Defaults to *27 000 (= 15
        min)*.
    """

    @staticmethod
    def get_default_settings() -> dict[str, Any]:
        """Get the default settings values as a dictionary."""
        default_settings = {
            "animal_type": AnimalType.MOUSE,
            "events": set(),
            "filter_flickering": False,
            "filter_stop": False,
            "fps": 30,
            "night_begin": 20,
            "night_duration": 12,
            "output_folder": None,
            "processing_limits": (None, None),
            "processing_window": oneDay,
            "rebuild_events": False,
            "time_window": 15 * oneMinute,
        }
        return default_settings

    @staticmethod
    def get_all_keys():
        """Get all settings names."""
        return [key for key in LMTEYESettings.get_default_settings()]

    @staticmethod
    def convert_in_str(initial_dict: dict[str, Any]) -> dict[str, Any]:
        """Convert the settings values in string for better readability."""
        new_dict = initial_dict.copy()

        new_dict["animal_type"] = new_dict["animal_type"].name

        if new_dict["output_folder"] is not None:
            new_dict["output_folder"] = str(new_dict["output_folder"])

        if isinstance(new_dict["events"], set):
            new_dict["events"] = list(new_dict["events"])

        new_dict["processing_limits"] = tuple(
            (
                ts.isoformat(sep=" ", timespec="seconds")
                if ts is not None
                else None
            )
            for ts in initial_dict["processing_limits"]
        )

        return new_dict

    @staticmethod
    def convert_from_str(initial_dict: dict[str, Any]) -> dict[str, Any]:
        """Convert the settings values from string to their original type."""
        new_dict = initial_dict.copy()

        new_dict["animal_type"] = AnimalType[new_dict["animal_type"]]

        if new_dict["output_folder"] is not None:
            new_dict["output_folder"] = Path(new_dict["output_folder"])

        if new_dict["events"] == [None]:
            new_dict["events"] = set()
        elif isinstance(new_dict["events"], list):
            new_dict["events"] = set(new_dict["events"])

        new_dict["processing_limits"] = tuple(
            pd.Timestamp(ts) if ts is not None else None
            for ts in initial_dict["processing_limits"]
        )

        return new_dict

    def __init__(self, **kwargs):
        """Initialize the settings with default or specified values."""
        self.reset()
        self.update_from_dict(kwargs)
        self._saver = ParameterSaver()

    def reset(self):
        """Reset the settings to their initial values."""

        default_settings = LMTEYESettings.get_default_settings()

        self.animal_type: AnimalType = default_settings["animal_type"]
        self.events: set[str] = default_settings["events"]
        self.filter_flickering: bool = default_settings["filter_flickering"]
        self.filter_stop: bool = default_settings["filter_stop"]
        self.fps: int = default_settings["fps"]
        self.night_begin: int = default_settings["night_begin"]
        self.night_duration: int = default_settings["night_duration"]
        self.output_folder: Path | None = default_settings["output_folder"]
        self.processing_window: int = default_settings["processing_window"]
        self.processing_limits: tuple[
            int | pd.Timestamp | None, int | pd.Timestamp | None
        ] = default_settings["processing_limits"]
        self.rebuild_events: bool = default_settings["rebuild_events"]
        self.time_window: int = default_settings["time_window"]

    def logic_update(self):
        """Update the settings values based on the current settings. Useful,
        for example, to add events if filters are activated."""
        # need to filter flickering
        if self.filter_flickering:
            self.events.add("Flickering")

        # always needed for activity analysis
        self.events.add("Stop")
        self.events.add("Stop in contact")
        self.events.add("Stop isolated")
        self.events.add("Move isolated")
        self.events.add("Move in contact")

    def get_as_dict(self) -> dict[str, Any]:
        """Get the settings as a dictionary."""
        settings = {}
        for key in LMTEYESettings.get_all_keys():
            settings[key] = getattr(self, key)
        return settings

    def get_as_str_dict(self):
        """Get the settings as a dictionary without class or object values
        (only int, float, bool, None and str). Useful for saving the settings in a JSON
        file."""
        return LMTEYESettings.convert_in_str(self.get_as_dict())

    def update_from_dict(self, settings_dict: dict[str, Any]):
        """Update the settings from a dictionary."""
        update_dict = self.get_as_dict()
        update_dict.update(settings_dict)

        for key in LMTEYESettings.get_all_keys():
            setattr(self, key, update_dict[key])

    def save(self, file_path: Path):
        """Save the settings to a JSON file."""

        if self._saver is None:
            raise ValueError(
                "No saver defined for LMT-EYE settings. Cannot save settings."
            )

        settings = self.get_as_str_dict()

        self._saver.set_values(settings)
        if file_path:
            self._saver.save(file_path)
        else:
            print("No file selected.")

    def load(self, file_path: Path):
        """Load the settings from a JSON file."""

        if self._saver is None:
            raise ValueError(
                "No saver defined for LMT-EYE settings. Cannot load settings."
            )

        self._saver.load(file_path)
        settings = self._saver.get_parameters()
        settings = LMTEYESettings.convert_from_str(settings)
        self.update_from_dict(settings)
