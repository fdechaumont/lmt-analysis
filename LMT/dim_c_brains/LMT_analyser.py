"""
@author: xmousset
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Literal

import pandas as pd

from dim_c_brains.scripts.parameter_saver import ParameterSaver
from dim_c_brains.scripts.reports_manager import HTMLReportManager
from dim_c_brains.scripts.data_extractor import DataFrameConstructor
from dim_c_brains.scripts.events_rebuilder import (
    RebuildOption,
    EventsRebuilder,
)
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


class AnalysisSettings:
    """Class to hold analysis settings."""

    @staticmethod
    def get_all_keys():
        """Get all attribute names except those starting with an underscore."""
        keys = [
            key
            for key in AnalysisSettings().__dict__
            if not key.startswith("_")
        ]
        return keys

    @staticmethod
    def convert_in_str(initial_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Convert the settings values in string for better readability."""
        new_dict = initial_dict.copy()

        new_dict["animal_type"] = new_dict["animal_type"].name

        if new_dict["output_folder"] is not None:
            new_dict["output_folder"] = str(new_dict["output_folder"])

        new_dict["rebuild_option"] = new_dict["rebuild_option"].name

        return new_dict

    @staticmethod
    def convert_from_str(initial_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Convert the settings values from string to their original type."""
        new_dict = initial_dict.copy()

        new_dict["animal_type"] = AnimalType[new_dict["animal_type"]]

        if new_dict["output_folder"] is not None:
            new_dict["output_folder"] = Path(new_dict["output_folder"])

        new_dict["rebuild_option"] = RebuildOption[new_dict["rebuild_option"]]

        return new_dict

    def __init__(self):
        """Initialize the settings with default values."""
        self.reset()
        self._saver = ParameterSaver()

    def reset(self):
        """Reset the settings to their initial values."""
        self.analysis_limits: List[int | str | None] = [None, None]
        self.animal_type: AnimalType = AnimalType.MOUSE
        self.events_in_overview: List[str] = []
        self.events_to_analyse: List[str] = []
        self.events_to_rebuild: List[str] = []
        self.filter_flickering: bool = False
        self.filter_stop: bool = False
        self.fps: int = 30
        self.night_begin: int = 20
        self.night_duration: int = 12
        self.output_folder: Path | None = None
        self.processing_window: int = oneDay
        self.rebuild_option: RebuildOption = RebuildOption.MISSING
        self.time_window: int = 15 * oneMinute

    def get_as_dict(self) -> Dict[str, Any]:
        """Get the settings as a dictionary."""
        settings = {}
        for key in self.get_all_keys():
            settings[key] = getattr(self, key)
        return settings

    def update_from_dict(self, settings_dict: Dict[str, Any]):
        """Update the settings from a dictionary."""
        update_dict = self.get_as_dict()
        update_dict.update(settings_dict)

        for key in self.get_all_keys():
            setattr(self, key, update_dict[key])

    def save(self, file_path: Path):
        """Save the settings to a JSON file."""

        if self._saver is None:
            raise ValueError(
                "No saver defined for AnalysisSettings. Cannot save settings."
            )

        settings = AnalysisSettings.convert_in_str(self.get_as_dict())

        self._saver.set_values(settings)
        if file_path:
            self._saver.save(file_path)
        else:
            print("No file selected.")

    def load(self, file_path: Path):
        """Load the settings from a JSON file."""

        if self._saver is None:
            raise ValueError(
                "No saver defined for AnalysisSettings. Cannot load settings."
            )

        self._saver.load(file_path)
        settings = self._saver.get_parameters()
        settings = AnalysisSettings.convert_from_str(settings)
        self.update_from_dict(settings)


class LMTAnalyser:

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

    def __init__(self, **kwargs):
        """
        Analysis workflow for LMT data. Can rebuild events, generate dataframes
        and generate HTML reports.

        Parameters
        ----------
        analysis_limits : tuple of (int or str or None, int or str or None), optional
            Start and end of the analysis period. Each can be an integer frame
            number or a timestamp string. Defaults to (None, None).
            *(timestamp string example: "2026-01-01 00:00:00")*
        database_path : Path, optional
            Path to the SQLite data file. If not provided, prompts user to
            select file.
        events_in_overview : list of str, optional
            List of event names for overview reports. By default, no overview
            event analysis is performed (None).
        events_to_analyse : list of str, optional
            List of event names to analyze. By default, no event analysis is
            performed (None).
        events_to_rebuild : list of str or None, optional
            List of event names to rebuild if `rebuild_option` is set to
            'custom', otherwise, it is filled automatically. By default, None.
        filter_flickering : bool, optional
            Whether to filter flickering activity. Defaults to False.
        filter_stop : bool, optional
            Whether to filter stop activity. Defaults to False.
        fps : int, optional
            Frame rate of the recording. Defaults to 30 *frames per second*.
        night_begin : int, optional
            Hour when the night begins. Defaults to 20 (8 *p.m.*).
        night_duration : int, optional
            Duration of the night in hours. Defaults to 12 (8 *p.m.* to 8
            *a.m.*).
        output_folder : Path or str or None, optional
            Folder to save the output reports. By default, prompts user to
            select folder ('manual selection').
        processing_window : int, optional
            Maximum processing duration in seconds. Defaults to 1 *day* (2 592
            000 *frames*).
        rebuild_option : RebuildOption, optional
            Rebuild option for events before analysis. Defaults to
            RebuildOption.MISSING.
            Possible values:
                - RebuildOption.ALL: rebuild all events that exist for LMT.
                - RebuildOption.MISSING: rebuild only missing events in
                    database.
                - RebuildOption.ANALYSIS: rebuild analysis-related events
                    (those in `LMTAnalyser.events_to_analyse`).
                - RebuildOption.CUSTOM: rebuild only events specified in
                    `LMTAnalyser.events_to_rebuild`.
        time_window : int, optional
            Time window in seconds for binning data. Defaults to 15 *min*
            (27 000 *frames*).
        """

        self.load_sqlite_file(kwargs.get("database_path", None))

        self.set_time_window(
            time_window=kwargs.get("time_window", 15 * oneMinute)
        )
        self.set_frame_rate(fps=kwargs.get("fps", 30))

        self.set_processing_window(
            processing_window=kwargs.get("processing_window", oneDay)
        )

        self.set_night_hours(
            night_begin=kwargs.get("night_begin", 20),
            night_duration=kwargs.get("night_duration", 12),
        )

        self.set_filters(
            flickering=kwargs.get("filter_flickering", True),
            stop=kwargs.get("filter_stop", True),
        )

        self.set_events_to_analyse(kwargs.get("events_to_analyse", None))

        self.set_events_in_overview(kwargs.get("events_in_overview", None))

        self.set_output_folder(output_folder=kwargs.get("output_folder", None))

        self.set_rebuild_option(
            rebuild_option=kwargs.get("rebuild_option", RebuildOption.MISSING)
        )

        rebuild_list = kwargs.get("events_to_rebuild", None)
        if (
            rebuild_list is not None
            and self.rebuild_option == RebuildOption.CUSTOM
        ):
            self.set_custom_rebuild(rebuild_list)

        self.set_analysis_limits(
            start=kwargs.get("start", None),
            end=kwargs.get("end", None),
        )

    def load_sqlite_file(self, database_path: Path | str | None):
        """Load the SQLite data file. If no file path is provided, prompts the
        user to select a file."""
        if isinstance(database_path, str):
            database_path = Path(database_path)
        if database_path is None:
            database_path = select_sqlite_file()
        self.database_path = database_path

    def set_events_to_analyse(self, event_list: list[str] | None):
        """Load the list of event names to analyze."""
        self.events_to_analyse: List[str] = []

        if event_list is not None:
            self.events_to_analyse = event_list

        if (
            "Flickering" not in self.events_to_analyse
            and self.filter_flickering
        ):
            self.events_to_analyse.append("Flickering")

        if "Stop" not in self.events_to_analyse and self.filter_stop:
            self.events_to_analyse.append("Stop")

        if (
            "Stop in contact" not in self.events_to_analyse
            and self.filter_stop
        ):
            self.events_to_analyse.append("Stop in contact")

        if "Stop isolated" not in self.events_to_analyse and self.filter_stop:
            self.events_to_analyse.append("Stop isolated")

    def set_events_in_overview(
        self, overview_card_event_list: list[str] | None
    ):
        """Set the list of event names for overview reports."""
        self.events_in_overview = overview_card_event_list

    def set_time_window(self, time_window: int):
        """Set the time window for data binning (in *frames*)."""
        self.time_window = time_window

    def set_frame_rate(self, fps: int):
        """Set the frame rate of the recording (in *frames per second*)."""
        self.fps = fps

    def set_processing_window(self, processing_window: int):
        """Set the maximum processing frame window to compute (in *frames*).
        If the data is longer than this window, the computation of the data
        will be splitted into chunks of this size."""
        self.processing_window = processing_window

    def set_night_hours(self, night_begin: int, night_duration: int):
        """Set the night period for the analysis.

        Parameters
        ----------
        night_begin : int
            Hour when the night begins (0-23).
        night_duration : int
            Duration of the night in hours.
        """
        self.night_begin = night_begin
        self.night_duration = night_duration

    def set_filters(self, flickering: bool = True, stop: bool = True):
        """Set the filters for activity analysis.

        Parameters
        ----------
        flickering : bool, optional
            Whether to filter the 'Flickering' event. Defaults to True.
        stop : bool, optional
            Whether to filter the 'Stop' event. Defaults to True.
        """
        self.filter_flickering = flickering
        self.filter_stop = stop

    def set_output_folder(
        self,
        output_folder: Path | str | Literal["manual_selection"] | None = None,
    ):
        """Set the output folder for saving reports. If 'manual_selection' is
        provided, prompts the user to select a folder. If None is provided,
        the output folder will the folder of the selected .sqlite file."""
        if isinstance(output_folder, str):
            if output_folder != "manual_selection":
                output_folder = Path(output_folder)
            else:
                output_folder = select_folder()
        self.output_folder = output_folder

    def set_rebuild_option(self, rebuild_option: RebuildOption):
        """Set the rebuild option for events before analysis.

        Args:
            rebuild_option (RebuildOption): rebuild option. Can be one of the following:
                - RebuildOption.ALL: rebuild all events that exist for LMT.
                - RebuildOption.MISSING: rebuild only missing events in database.
                - RebuildOption.ANALYSIS: rebuild analysis-related events (those in
                    `events_to_analyse`).
                - RebuildOption.CUSTOM: rebuild only events specified in
                    `events_to_rebuild`.
        """
        self.rebuild_option = rebuild_option

        match self.rebuild_option:
            case RebuildOption.NO_REBUILD:
                self.events_to_rebuild = None

            case RebuildOption.ANALYSIS:
                self.events_to_rebuild = self.events_to_analyse

            case RebuildOption.MISSING:
                # Handled by EventsRebuilder
                self.events_to_rebuild = ["auto_missing"]

            case RebuildOption.ALL:
                # Handled by EventsRebuilder
                self.events_to_rebuild = ["auto_all"]

            case RebuildOption.CUSTOM:
                self.events_to_rebuild = []

    def set_custom_rebuild(self, events_to_rebuild: List[str]):
        """Set the rebuild list of event names and set the rebuild option to
        CUSTOM."""
        self.rebuild_option = RebuildOption.CUSTOM
        self.events_to_rebuild = events_to_rebuild

    def set_analysis_limits(
        self, start: int | str | None, end: int | str | None
    ):
        """Set the analysis limits for the data.

        Parameters
        ----------
        start : int or str or None
            Start of the analysis period. Can be an integer frame number or a
            timestamp string. Defaults to None. *(timestamp string example:
            "2026-01-01 00:00:00")*
        end : int or str or None
            End of the analysis period. Can be an integer frame number or a
            timestamp string. Defaults to None.*(timestamp string example:
            "2026-01-01 00:00:00")*
        """

        if start is not None and end is not None and type(start) != type(end):
            raise ValueError(
                f"set_analysis_limits inputs must be of the same type "
                f"({type(start)} != {type(end)})"
            )

        if isinstance(start, str):
            new_start = pd.Timestamp(start)
        else:
            new_start = start

        if isinstance(end, str):
            new_end = pd.Timestamp(end)
        else:
            new_end = end

        self.analysis_limits = (new_start, new_end)

    def get_parameters(self):
        """Get the current analysis parameters. Useful for kwargs passing
        arguments."""
        parameters: Dict[str, Any] = {}

        parameters["analysis_limits"] = self.analysis_limits

        parameters["database_path"] = self.database_path

        parameters["rebuild_option"] = self.rebuild_option

        parameters["events_to_rebuild"] = self.events_to_rebuild
        parameters["events_to_analyse"] = self.events_to_analyse
        parameters["events_in_overview"] = self.events_in_overview

        parameters["time_window"] = self.time_window
        parameters["processing_window"] = self.processing_window

        parameters["output_folder"] = self.output_folder

        parameters["fps"] = self.fps

        parameters["filter_stop"] = self.filter_stop
        parameters["filter_flickering"] = self.filter_flickering

        parameters["night_begin"] = self.night_begin
        parameters["night_duration"] = self.night_duration

        return parameters

    def rebuild_database(self):
        """Rebuild events in the database according to the selected rebuild
        option."""
        connection = sqlite3.connect(str(self.database_path))

        rebuilder = EventsRebuilder(
            connection,
            str(self.database_path),
            self.rebuild_option,
            self.events_to_rebuild,
            self.processing_window,
            self.analysis_limits[0],
            self.analysis_limits[1],
        )
        rebuilder.rebuild()
        connection.close()

    def run_analysis(self):
        """Run the analysis workflow, generating dataframes and HTML reports.
        Save the reports to the selected output folder."""
        connection = sqlite3.connect(str(self.database_path))
        repo_manager = HTMLReportManager()

        df_constructor = DataFrameConstructor(
            connection,
            bin_window=self.time_window,
            processing_window=self.processing_window,
            start=self.analysis_limits[0],
            end=self.analysis_limits[1],
        )

        df_constructor.binner.set_parameters(
            fps=self.fps,
        )

        df_dic: Dict[str, pd.DataFrame | None] = {}
        df_dic["activity"] = activity_reports.generic_reports(
            repo_manager, df_constructor, **self.get_parameters()
        )

        if self.events_to_analyse is None:
            df_dic["events"] = None
        else:
            df_dic["events"] = pd.DataFrame()
            for event_name in self.events_to_analyse:
                df_dic["events"] = pd.concat(
                    [
                        df_dic["events"],
                        event_reports.generic_reports(
                            repo_manager,
                            df_constructor,
                            event_name=event_name,
                            **self.get_parameters(),
                        ),
                    ]
                )

        df_dic["sensors"] = sensors_reports.generic_reports(
            repo_manager, df_constructor, **self.get_parameters()
        )

        df_dic["mice"] = overview_reports.generic_reports(
            repo_manager,
            df_constructor,
            df_activity=df_dic["activity"],
            df_events=df_dic["events"],
            df_sensors=df_dic["sensors"],
            **self.get_parameters(),
        )

        self.set_output_folder(self.output_folder)

        if self.output_folder:
            repo_manager.generate_local_output(self.output_folder)
            print(f"Save analysis at\n{self.output_folder}")
        else:
            output_folder = self.database_path.parent / (
                self.database_path.stem + " - analysis"
            )
            print(f"Save analysis to default folder\n{output_folder}")

        return df_dic
