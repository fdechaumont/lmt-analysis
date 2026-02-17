"""
@author: xmousset
"""

import sqlite3
from typing import Any
from pathlib import Path

import pandas as pd

from dim_c_brains.scripts.parameter_saver import ParameterSaver
from dim_c_brains.scripts.reports_manager import HTMLReportManager
from dim_c_brains.scripts.data_extractor import DataFrameConstructor
from dim_c_brains.scripts.events_rebuilder import EventsRebuilder
from dim_c_brains.reports import (
    activity_reports,
    event_reports,
    overview_reports,
    sensors_reports,
)
from dim_c_brains.scripts.tkinter_tools import (
    select_sqlite_file,
    select_folder,
)

from lmtanalysis.Animal import AnimalType
from lmtanalysis.Measure import oneMinute, oneDay


class LMTSettings:
    """Manage parameters for LMT analysis workflow.

    Parameters
    ----------
    analysis_limits : tuple of (int or str or None, int or str or None), optional
        Start and end of the analysis period. Each can be an integer frame
        number or a timestamp string. Defaults to (None, None).
        *(timestamp string example: "2026-01-01 00:00:00")*
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
            "analysis_limits": (None, None),
            "animal_type": AnimalType.MOUSE,
            "events": set(),
            "filter_flickering": False,
            "filter_stop": False,
            "fps": 30,
            "night_begin": 20,
            "night_duration": 12,
            "output_folder": None,
            "processing_window": 30 * oneDay,
            "rebuild_events": False,
            "time_window": 15 * oneMinute,
        }
        return default_settings

    @staticmethod
    def get_all_keys():
        """Get all settings names."""
        return [key for key in LMTSettings.get_default_settings()]

    @staticmethod
    def convert_in_str(initial_dict: dict[str, Any]) -> dict[str, Any]:
        """Convert the settings values in string for better readability."""
        new_dict = initial_dict.copy()

        new_dict["animal_type"] = new_dict["animal_type"].name

        if new_dict["output_folder"] is not None:
            new_dict["output_folder"] = str(new_dict["output_folder"])

        if isinstance(new_dict["events"], set):
            new_dict["events"] = list(new_dict["events"])

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

        print(f"Converted settings from str: {new_dict}")

        return new_dict

    def __init__(self, **kwargs):
        """Initialize the settings with default or specified values."""
        self.reset()
        self.update_from_dict(kwargs)
        self._saver = ParameterSaver()

    def reset(self):
        """Reset the settings to their initial values."""

        default_settings = LMTSettings.get_default_settings()

        self.analysis_limits: tuple[int | str | None, int | str | None] = (
            default_settings["analysis_limits"]
        )
        self.animal_type: AnimalType = default_settings["animal_type"]
        self.events: set[str] = default_settings["events"]
        self.filter_flickering: bool = default_settings["filter_flickering"]
        self.filter_stop: bool = default_settings["filter_stop"]
        self.fps: int = default_settings["fps"]
        self.night_begin: int = default_settings["night_begin"]
        self.night_duration: int = default_settings["night_duration"]
        self.output_folder: Path | None = default_settings["output_folder"]
        self.processing_window: int = default_settings["processing_window"]
        self.rebuild_events: bool = default_settings["rebuild_events"]
        self.time_window: int = default_settings["time_window"]

    def logic_update(self):
        """Update the settings values based on the current settings. Useful,
        for example, to add events if filters are activated."""
        if self.filter_flickering:
            self.events.add("Flickering")

        if self.filter_stop:
            self.events.add("Stop")
            self.events.add("Stop in contact")
            self.events.add("Stop isolated")

    def get_as_dict(self) -> dict[str, Any]:
        """Get the settings as a dictionary."""
        settings = {}
        for key in LMTSettings.get_all_keys():
            settings[key] = getattr(self, key)
        return settings

    def update_from_dict(self, settings_dict: dict[str, Any]):
        """Update the settings from a dictionary."""
        update_dict = self.get_as_dict()
        update_dict.update(settings_dict)

        for key in LMTSettings.get_all_keys():
            setattr(self, key, update_dict[key])

    def save(self, file_path: Path):
        """Save the settings to a JSON file."""

        if self._saver is None:
            raise ValueError(
                "No saver defined for LMTSettings. Cannot save settings."
            )

        settings = LMTSettings.convert_in_str(self.get_as_dict())

        self._saver.set_values(settings)
        if file_path:
            self._saver.save(file_path)
        else:
            print("No file selected.")

    def load(self, file_path: Path):
        """Load the settings from a JSON file."""

        if self._saver is None:
            raise ValueError(
                "No saver defined for LMTSettings. Cannot load settings."
            )

        self._saver.load(file_path)
        settings = self._saver.get_parameters()
        settings = LMTSettings.convert_from_str(settings)
        self.update_from_dict(settings)


class LMTDataAnalyzer:
    """Class to analyze LMT data, generate reports and save them to an output
    folder."""

    @staticmethod
    def get_informations(database_path: Path):
        """Get basic information about the experiment stored in the database.
        Returns a dictionary with keys:
            - 'n_animals': number of animals in the experiment.
            - 'start_time': start time of the experiment (pd.Timestamp).
            - 'end_time': end time of the experiment (pd.Timestamp).
            - 'duration': duration of the experiment (pd.Timedelta).
        """
        connection = sqlite3.connect(str(database_path))

        query = """
            SELECT
                COUNT(DISTINCT RFID) AS n_animals,
                (SELECT FRAMENUMBER FROM FRAME ORDER BY FRAMENUMBER ASC LIMIT 1) AS first_frame,
                (SELECT TIMESTAMP FROM FRAME ORDER BY FRAMENUMBER ASC LIMIT 1) AS first_timestamp,
                (SELECT FRAMENUMBER FROM FRAME ORDER BY FRAMENUMBER DESC LIMIT 1) AS last_frame,
                (SELECT TIMESTAMP FROM FRAME ORDER BY FRAMENUMBER DESC LIMIT 1) AS last_timestamp
            FROM ANIMAL;
        """
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        n_animals: int = result[0]
        start_frame: int = result[1]
        start_timestamp: int = result[2]
        end_frame: int = result[3]
        end_timestamp: int = result[4]
        start_time: pd.Timestamp = pd.to_datetime(start_timestamp, unit="ms")
        end_time: pd.Timestamp = pd.to_datetime(end_timestamp, unit="ms")
        duration: pd.Timedelta = end_time - start_time
        fps = (end_frame - start_frame) / duration.total_seconds()

        connection.close()

        info = {
            "database_name": database_path.stem,
            "n_animals": n_animals,
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration,
            "fps": fps,
        }
        return info

    def __init__(
        self,
        database_path: Path | str | None = None,
        settings: LMTSettings | None = None,
    ):
        """
        Analysis workflow for LMT data. Can rebuild events, generate dataframes
        and generate HTML reports.

        Parameters
        ----------
        database_path : Path, optional
            Path to the SQLite data file. If not provided, prompts user to
            select file.
        settings : LMTSettings, optional
            Analysis settings. If not provided, defaults to a new instance
            of LMTSettings.
        """
        if isinstance(database_path, str):
            database_path = Path(database_path)
        self.database_path = database_path
        if database_path is None:
            self.database_path = self.choose_sqlite_file()

        if settings is None:
            self.settings = LMTSettings()
        else:
            self.settings = settings

    def choose_sqlite_file(self):
        """Load the SQLite data file. If no file path is provided, prompts the
        user to select a file."""
        database_path = select_sqlite_file()
        if database_path is None:
            return
        self.database_path = database_path

    def choose_output_folder(self, output_folder: Path | str | None = None):
        """Choose the output folder for the analysis reports. If no folder path
        is provided, prompts the user to select a folder."""
        output_folder = select_folder()
        if output_folder is None:
            return
        self.settings.output_folder = output_folder

    def _convert_analysis_limits(self):
        """Get the analysis limits values in frames."""

        start_f, end_f = self.settings.analysis_limits

        if (
            start_f is not None
            and end_f is not None
            and type(start_f) != type(end_f)
        ):
            raise ValueError(
                f"set_analysis_limits inputs must be of the same type "
                f"({type(start_f)} != {type(end_f)})"
            )

        if isinstance(start_f, str):
            new_start = pd.Timestamp(start_f)
        else:
            new_start = start_f

        if isinstance(end_f, str):
            new_end = pd.Timestamp(end_f)
        else:
            new_end = end_f

        return (new_start, new_end)

    def rebuild_database(self):
        """Rebuild events in the database according to the selected rebuild
        option."""
        connection = sqlite3.connect(str(self.database_path))

        start, end = self._convert_analysis_limits()

        rebuilder = EventsRebuilder(
            connection,
            str(self.database_path),
            self.settings.processing_window,
            start,
            end,
            self.settings.animal_type,
        )
        self.settings.logic_update()
        if self.settings.rebuild_events:
            events_to_rebuild = self.settings.events
        else:
            events_to_rebuild = (
                self.settings.events - rebuilder.get_events_in_database()
            )

        rebuilder.rebuild(events_to_rebuild)
        connection.close()

    def run_analysis(self):
        """Run the analysis workflow, generating dataframes and HTML reports.
        Save the reports to the selected output folder."""

        if self.database_path is None:
            raise ValueError("No database path provided for analysis.")

        self.settings.logic_update()

        connection = sqlite3.connect(str(self.database_path))
        repo_manager = HTMLReportManager()

        start, end = self._convert_analysis_limits()
        df_constructor = DataFrameConstructor(
            connection,
            self.settings.time_window,
            self.settings.processing_window,
            start,
            end,
        )

        df_constructor.binner.set_parameters(
            fps=self.settings.fps,
        )

        activity_df = activity_reports.generic_reports(
            repo_manager, df_constructor, **self.settings.get_as_dict()
        )

        if not self.settings.events:
            events_df = None
        else:
            events_df = pd.DataFrame()
            for event_name in self.settings.events:
                events_df = pd.concat(
                    [
                        events_df,
                        event_reports.generic_reports(
                            repo_manager,
                            df_constructor,
                            event_name=event_name,
                            **self.settings.get_as_dict(),
                        ),
                    ]
                )

        sensors_df = sensors_reports.generic_reports(
            repo_manager, df_constructor, **self.settings.get_as_dict()
        )

        animal_df = overview_reports.generic_reports(
            repo_manager,
            df_constructor,
            df_activity=activity_df,
            df_events=events_df,
            df_sensors=sensors_df,
            **self.settings.get_as_dict(),
        )

        if self.settings.output_folder is None:
            self.settings.output_folder = self.database_path.parent / (
                self.database_path.stem + " - analysis"
            )

        print(f"Saving in \n{self.settings.output_folder}")
        repo_manager.generate_local_output(self.settings.output_folder)

        results_df: list[pd.DataFrame | None] = [
            activity_df,
            events_df,
            sensors_df,
            animal_df,
        ]

        return results_df

    def open_analysis_output(self):
        """Open the generated analysis output in the default web browser."""
        if self.settings.output_folder is None:
            raise ValueError(
                "Output folder is not defined. Please run the analysis first "
                "to generate the output folder."
            )

        index_file = self.settings.output_folder / "index.html"
        if index_file.exists():
            HTMLReportManager.open_local_output(self.settings.output_folder)
        else:
            print(f"Output file not found: {index_file}")
