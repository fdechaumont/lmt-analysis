"""
@creation: 26-01-2026
@author: xmousset
"""

import sys
import traceback
from types import ModuleType
from sqlite3 import Connection
from typing import Any, Literal

import pandas as pd

from dim_c_brains.scripts.binner import Binner
from dim_c_brains.scripts.events_and_modules import get_modules

from lmtanalysis.Animal import AnimalPool
from lmtanalysis.AnimalType import AnimalType
from lmtanalysis.Event import Chronometer
from lmtanalysis.Measure import oneDay
from lmtanalysis import BuildDataBaseIndex, CheckWrongAnimal
from lmtanalysis.TaskLogger import TaskLogger
from lmtanalysis.EventTimeLineCache import (
    flushEventTimeLineCache,
    disableEventTimeLineCache,
)

from psutil import virtual_memory


class EventsRebuilder:
    def __init__(
        self,
        connection: Connection,
        database_path: Any,
        animal_type: AnimalType = AnimalType.MOUSE,
        start: int | pd.Timestamp | None = None,
        end: int | pd.Timestamp | None = None,
        fps: int = 30,
        processing_window: int = oneDay,
    ):
        """Class to handle the rebuilding of events in the database.

        Args:
            connection (Connection): SQLite database connection.
            database_path (Any): The path to the database file.
            animal_type (AnimalType): Type of animal for event processing.
            start (int | pd.Timestamp | None): Start limit for analysis.
                Can be in frames (int) or timestamps (pd.Timestamp).
            end (int | pd.Timestamp | None): End limit for analysis.
                Can be in frames (int) or timestamps (pd.Timestamp).
            fps (int): Frame rate of the recording in frames per second.
                Default is 30.
            processing_window (int): Processing window size in frames.
                Default is one day (in frames).
        """
        self.conn = connection
        self.database_path = database_path
        self.animal_type = animal_type

        last_framenumber, last_timestamp = Binner.get_last_frame(self.conn)
        self.binner = Binner(
            last_framenumber,
            last_timestamp,
            bin_size=processing_window,
            start=start,
            end=end,
            fps=fps,
        )

    def get_events_in_database(self) -> set[str]:
        """Get the list of existing events in the SQLite database."""
        query = "SELECT DISTINCT NAME FROM EVENT ORDER BY NAME"

        cursor = self.conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()

        database_events = set([row[0] for row in results])
        return database_events

    def set_processing_window(self, processing_window: int):
        """Set the processing window (in *frames*) for processing."""
        self.binner.set_parameters(bin_size=processing_window)

    def get_processing_window(self, unit: Literal["FRAME", "TIME"] = "FRAME"):
        """Get the processing window (data chunk size)."""
        if unit == "FRAME":
            return self.binner.bin_size
        elif unit == "TIME":
            return self.binner.frames_to_timedelta(self.binner.bin_size)
        else:
            raise ValueError("Invalid unit. Choose 'FRAME' or 'TIME'.")

    def set_processing_limits(
        self,
        start: int | pd.Timestamp | None = None,
        end: int | pd.Timestamp | None = None,
    ):
        """Set the processing limits for data processing from frames or
        timestamps."""

        self.binner.set_parameters(start=start, end=end)

    def get_processing_limits(
        self, unit: Literal["FRAME", "TIME"] = "FRAME"
    ) -> tuple[int | pd.Timestamp, int | pd.Timestamp]:
        """Get the processing frame limits."""
        if unit == "FRAME":
            return (self.binner.start_frame, self.binner.end_frame)
        elif unit == "TIME":
            start_time = self.binner.frame_to_time(self.binner.start_frame)
            end_time = self.binner.frame_to_time(self.binner.end_frame)
            return (start_time, end_time)
        else:
            raise ValueError("Invalid unit. Choose 'FRAME' or 'TIME'.")

    def check_memory(self):
        """Check available system memory and disable event caching if
        necessary."""
        mem = virtual_memory()
        availableMemoryGB = mem.total / 1_000_000_000
        print("Total memory on computer: (GB)", availableMemoryGB)

        if availableMemoryGB < 10:
            print("Not enough memory to use cache load of events.")
            disableEventTimeLineCache()

    def _rebuild_window(
        self, modules: set[ModuleType], window: tuple[int, int]
    ):
        """Rebuild events in the specified time window using the specified
        modules."""

        if not modules:
            print("Empty module list. Flushing not necessary.")
            return

        CheckWrongAnimal.check(self.conn, window[0], window[1])

        animalPool = None
        flushEventTimeLineCache()
        print("Caching load of animal detection...")
        animalPool = AnimalPool()
        animalPool.loadAnimals(self.conn)
        animalPool.loadDetection(start=window[0], end=window[1])
        print("Caching load of animal detection done.")

        for build_event_module in modules:

            event_chrono = Chronometer(str(build_event_module))
            build_event_module.reBuildEvent(
                self.conn,
                self.database_path,
                tmin=window[0],
                tmax=window[1],
                pool=animalPool,
                animalType=self.animal_type,
            )
            event_chrono.printTimeInS()

    def rebuild(self, events: list[str] | set[str]):
        """Rebuild events in the database from 'self.start' to 'self.end' using
        the specified modules."""
        if not events:
            print("No events to rebuild.")
            return

        modules = get_modules(events)

        self.check_memory()
        chrono = Chronometer("ReBuild events")

        # update missing fields
        try:
            cursor = self.conn.cursor()
            query = "ALTER TABLE EVENT ADD METADATA TEXT"
            cursor.execute(query)
            self.conn.commit()
        except:
            print("METADATA field already exists")

        BuildDataBaseIndex.buildDataBaseIndex(self.conn, force=False)

        try:
            chrono = Chronometer("Flushing events")
            for module in modules:
                module.flush(self.conn)
            chrono.printTimeInS()

            for window in self.binner.get_bin_iterator():
                window_chrono = Chronometer(
                    "File "
                    + self.database_path
                    + " from "
                    + str(window[0])
                    + " to "
                    + str(window[1])
                )
                self._rebuild_window(modules, window)
                window_chrono.printTimeInS()

            print("Full file process time: ")
            chrono.printTimeInS()

        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(
                exc_type, exc_value, exc_traceback
            )
            error = "".join("!! " + line for line in lines)

            t = TaskLogger(self.conn)
            t.addLog(error)
            flushEventTimeLineCache()

            print(error, file=sys.stderr)
            raise Exception()

        print("\n*** REBUILD FINISHED ***\n")
