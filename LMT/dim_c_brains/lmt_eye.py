"""
@author: xmousset
"""

import sqlite3
from pathlib import Path

import pandas as pd

from dim_c_brains.lmt_eye_settings import LMTEYESettings
from dim_c_brains.scripts.reports_manager import HTMLReportManager
from dim_c_brains.scripts.dataframe_constructor import DataFrameConstructor
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


class LMTEYEDataAnalyzer:
    """Class to analyze LMT-EYE data, generate reports and save them to an output
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
        settings: LMTEYESettings | None = None,
    ):
        """
        LMT-EYE analysis workflow for LMT database. Can rebuild events,
        generate dataframes and HTML reports.

        Parameters
        ----------
        database_path : Path, optional
            Path to the SQLite data file. If not provided, prompts user to
            select file.
        settings : LMTEYESettings, optional
            Analysis settings. If not provided, defaults to a new instance
            of LMTEYESettings.
        """
        if isinstance(database_path, str):
            database_path = Path(database_path)
        self.database_path = database_path
        if database_path is None:
            self.database_path = self.choose_sqlite_file()

        if settings is None:
            self.settings = LMTEYESettings()
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

    def rebuild_database(self):
        """Rebuild events in the database according to the selected rebuild
        option."""
        connection = sqlite3.connect(str(self.database_path))

        rebuilder = EventsRebuilder(
            connection,
            str(self.database_path),
            self.settings.animal_type,
            self.settings.processing_limits[0],
            self.settings.processing_limits[1],
            self.settings.fps,
            self.settings.processing_window,
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

        print(
            f"Limits: {self.settings.processing_limits[0]}, "
            f"{self.settings.processing_limits[1]}"
        )

        df_constructor = DataFrameConstructor(
            connection,
            self.settings.time_window,
            self.settings.processing_window,
            self.settings.processing_limits[0],
            self.settings.processing_limits[1],
            self.settings.fps,
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
