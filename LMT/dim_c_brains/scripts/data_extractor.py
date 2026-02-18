"""
@author: xmousset
"""

import numpy as np
import pandas as pd
from typing import Any, Literal

from sqlite3 import Connection

from dim_c_brains.scripts.binner import Binner

from lmtanalysis.Measure import oneMinute, oneHour, oneDay
from lmtanalysis.Event import EventTimeLine
from lmtanalysis.Animal import Animal, AnimalPool


class DataFrameConstructor:
    """A class to construct pandas DataFrames from AnimalPool easy
    data manipulation and analysis. It is designed to handle large time
    windows (> oneDay), by processing data in chunks to reduce memory usage. By
    default, chunk size is set to one day.
    """

    def __init__(
        self,
        connection: Connection,
        bin_window: int = 15 * oneMinute,
        processing_window: int = oneDay,
        start: int | pd.Timestamp | None = None,
        end: int | pd.Timestamp | None = None,
    ):
        """
        instanciate pandas dataframes constructor. All datas will be binned
        according to the bin window provided (15 minutes by default) and will
        be processed in chunks of specified size (1 day by default).

        Args:
            connection (Connection): SQLite database connection.
            bin_window (int, optional): The bin window (in frames) for\
                binning data. Defaults to 15 minutes.
            processing_window (int, optional): The size (in frames) of each\
            data chunk to load into memory. Defaults to 1 day.
        """
        self.animal_pool = AnimalPool()
        self.animal_pool.loadAnimals(connection)

        self._init_binner()
        self.set_bin_window(bin_window)
        self.set_analysis_limits(start, end)
        self.processing_window = processing_window

    def _init_binner(self):
        """Initialize the DatetimeBinner object to compute the time bins."""
        query = "SELECT FRAMENUMBER, TIMESTAMP FROM FRAME ORDER BY FRAMENUMBER DESC LIMIT 1"
        cursor = self.animal_pool.conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()

        if not result:
            raise ValueError("No data found in FRAME table")

        lastframe, timestamp = result
        self.binner = Binner(lastframe, timestamp)

    def set_bin_window(self, bin_window: int):
        """Set the bin window (in *frames*) for data binning."""
        self.binner.set_parameters(bin_window)

    def get_bin_window(self, unit: Literal["FRAME", "TIME"] = "FRAME"):
        """Get the bin window for data analysis."""
        if unit == "FRAME":
            return self.binner.bin_size
        elif unit == "TIME":
            return self.binner.frames_to_timedelta(self.binner.bin_size)
        else:
            raise ValueError("Invalid unit. Choose 'FRAME' or 'TIME'.")

    def set_processing_window(self, processing_window: int):
        """Set the processing window (in *frames*) for data chunking."""
        self.processing_window = processing_window

    def get_processing_window(self, unit: Literal["FRAME", "TIME"] = "FRAME"):
        """Get the current processing window for data chunking."""
        if unit == "FRAME":
            return self.processing_window
        elif unit == "TIME":
            return self.binner.frames_to_timedelta(self.processing_window)
        else:
            raise ValueError("Invalid unit. Choose 'FRAME' or 'TIME'.")

    def set_analysis_limits(
        self,
        start: int | pd.Timestamp | None = None,
        end: int | pd.Timestamp | None = None,
    ):
        """Set the analysis limits for data processing from frames or
        timestamps."""

        if isinstance(start, pd.Timestamp):
            f_start = self.binner.time_to_frame(start)
        else:
            f_start = start

        if isinstance(end, pd.Timestamp):
            f_end = self.binner.time_to_frame(end)
        else:
            f_end = end

        self.binner.set_parameters(start_frame=f_start, end_frame=f_end)

    def get_analysis_limits(
        self, unit: Literal["FRAME", "TIME"] = "FRAME"
    ) -> tuple[Any, Any]:
        """Get the analysis frame limits.

        Returns:
            tuple: The start and end limits in the specified unit.
            It is either in frames (int) or timestamps (pd.Timestamp).
        """
        if unit == "FRAME":
            return (self.binner.start_frame, self.binner.end_frame)
        elif unit == "TIME":
            start_time = self.binner.frame_to_time(self.binner.start_frame)
            end_time = self.binner.frame_to_time(self.binner.end_frame)
            return (start_time, end_time)
        else:
            raise ValueError("Invalid unit. Choose 'FRAME' or 'TIME'.")

    def get_df_animals(self):
        """Get a DataFrame containing basic information about all animals."""
        print(f"Creating ANIMALS dataframe")
        df = pd.read_sql("SELECT * FROM ANIMAL", self.animal_pool.conn)

        return df

    def count_event_per_bin(
        self,
        animal: Animal,
        event: str,
        bin_iterator: list[tuple[int, int]],
    ):
        """Count occurrences of a specific event according to binning.

        Returns
        -------
        tuple of two lists (counts, durations)
            counts : list[int]
                Number of occurrences of the event in each bin.
            durations : list[int]
                Total duration (in frames) of the event in each bin.
        """

        event_timeline = EventTimeLine(
            self.animal_pool.conn,
            event,
            idA=animal.baseId,
            minFrame=bin_iterator[0][0],
            maxFrame=bin_iterator[-1][1],
        )

        counts: list[int] = []
        durations: list[int] = []
        for f_min, f_max in bin_iterator:
            counts.append(event_timeline.getNumberOfEvent(f_min, f_max))
            durations.append(
                event_timeline.getTotalDurationEvent(f_min, f_max)
            )

        return (counts, durations)

    def get_df_event(
        self, event: str, bin_iterator: list[tuple[int, int]] | None = None
    ):
        """Get a DataFrame containing event counts and durations for specified
        event and bin_iterator.
        """
        if bin_iterator is None:
            bin_iterator = self.binner.get_bin_iterator()

        results = []
        for animal in self.animal_pool.getAnimalList():
            print(
                f"Creating EVENT dataframe ({event}) "
                f"for animal {animal.RFID}"
            )

            counts, durations = self.count_event_per_bin(
                animal, event, bin_iterator
            )

            for i in range(len(bin_iterator)):
                results.append(
                    {
                        "RFID": animal.RFID,
                        "ANIMALID": animal.baseId,
                        "EVENT": event,
                        "START_FRAME": bin_iterator[i][0],
                        "END_FRAME": bin_iterator[i][1],
                        "START_TIME": self.binner.frame_to_time(
                            bin_iterator[i][0]
                        ),
                        "END_TIME": self.binner.frame_to_time(
                            bin_iterator[i][1]
                        ),
                        "EVENT_COUNT": counts[i],
                        "FRAME_COUNT": durations[i],
                        "DURATION": durations[i]
                        / self.binner.fps
                        / 60,  # in minutes
                    }
                )

        df = pd.DataFrame(results)
        return df

    def process_event(self, event: str):
        """Process data between start and end frames to get a DataFrame
        containing the specified event counts and durations. It will process
        the whole dataset using the process window.
        """

        split_iterator = self.binner.split_iterator_in_chunks(
            self.processing_window, self.binner.get_bin_iterator()
        )
        df = None

        for bin_iterator in split_iterator:
            print(
                f"EVENT processing ({event}) for frames {bin_iterator[0][0]} to "
                f"{bin_iterator[-1][1]}"
            )
            processed_df = self.get_df_event(event, bin_iterator)
            if df is None:
                df = processed_df
            else:
                df = pd.concat([df, processed_df], ignore_index=True)

        if df is None:
            raise ValueError("Unable to create a dataframe")

        return self.sort_rfid_as_category(df)

    def get_df_activity(
        self,
        bin_iterator: list[tuple[int, int]] | None = None,
        filter_flickering: bool = False,
        filter_stop: bool = False,
    ):
        """Get a DataFrame containing activity data for all animals. Can apply
        filters to exclude flickering and stop from distance and speed
        calculation. (distance are in cm and speed are in cm/s)

        It include distance, speed, move time and stop time
        binned according to the time window.
        """
        if bin_iterator is None:
            bin_iterator = self.binner.get_bin_iterator()

        self.animal_pool.loadDetection(
            start=bin_iterator[0][0],
            end=bin_iterator[-1][1],
            lightLoad=True,
        )

        results = []
        for animal in self.animal_pool.getAnimalList():
            print(f"Creating ACTIVITY dataframe for animal {animal.RFID}")

            stop_counts, stop_durations = self.count_event_per_bin(
                animal, "Stop", bin_iterator
            )

            move_iso_counts, move_iso_durations = self.count_event_per_bin(
                animal, "Move isolated", bin_iterator
            )

            move_inc_counts, move_inc_durations = self.count_event_per_bin(
                animal, "Move in contact", bin_iterator
            )

            distances = animal.getDistancePerBin(
                binIterator=bin_iterator,
                filter_flickering=filter_flickering,
                filter_stop=filter_stop,
            )
            speeds = animal.getSpeedPerBin(
                binIterator=bin_iterator,
                filter_flickering=filter_flickering,
                filter_stop=filter_stop,
            )

            for i in range(len(bin_iterator)):
                results.append(
                    {
                        "RFID": animal.RFID,
                        "ANIMALID": animal.baseId,
                        "START_FRAME": bin_iterator[i][0],
                        "END_FRAME": bin_iterator[i][1],
                        "START_TIME": self.binner.frame_to_time(
                            bin_iterator[i][0],
                        ),
                        "END_TIME": self.binner.frame_to_time(
                            bin_iterator[i][1],
                        ),
                        "DISTANCE": distances[i],
                        "SPEED_MEAN": speeds[i][0],
                        "SPEED_MIN": speeds[i][1],
                        "SPEED_MAX": speeds[i][2],
                        "SPEED_SUM": speeds[i][3],
                        "SPEED_STD": speeds[i][4],
                        "SPEED_SEM": speeds[i][5],
                        "STOP_COUNT": stop_counts[i],
                        "STOP_DURATION": stop_durations[i]
                        / self.binner.fps
                        / 60,  # in minutes
                        "MOVE_COUNT": move_iso_counts[i] + move_inc_counts[i],
                        "MOVE_DURATION": (
                            move_iso_durations[i] + move_inc_durations[i]
                        )
                        / self.binner.fps
                        / 60,  # in minutes
                        "UNDETECTED_DURATION": (
                            bin_iterator[i][1]
                            - bin_iterator[i][0]
                            - stop_durations[i]
                            - (move_iso_durations[i] + move_inc_durations[i])
                        )
                        / self.binner.fps
                        / 60,  # in minutes
                    }
                )

        df = pd.DataFrame(results)
        return df

    def process_activity(
        self,
        filter_flickering: bool = False,
        filter_stop: bool = False,
    ):
        """Process data between start and end frames to get a DataFrame
        containing activity data. It will process the whole dataset using
        the process window.
        """
        split_iterator = self.binner.split_iterator_in_chunks(
            self.processing_window, self.binner.get_bin_iterator()
        )
        df = None

        for bin_iterator in split_iterator:
            print(
                f"ACTIVITY processing for frames {bin_iterator[0][0]} to "
                f"{bin_iterator[-1][1]}"
            )
            processed_df = self.get_df_activity(
                bin_iterator, filter_flickering, filter_stop
            )
            if df is None:
                df = processed_df
            else:
                df = pd.concat([df, processed_df], ignore_index=True)

        if df is None:
            raise ValueError("Unable to create a dataframe")

        return self.sort_rfid_as_category(df)

    def sort_rfid_as_category(self, df: pd.DataFrame) -> pd.DataFrame:
        """Set the RFID column as a categorical data (sorted) type for better
        performance in plotting and analysis.

        Args:
            df (pd.DataFrame): The input DataFrame with an 'RFID' column.

        Returns:
            pd.DataFrame: The modified DataFrame with 'RFID' as a category.
        """
        sorted_rfids = sorted(df["RFID"].unique())
        df["RFID"] = pd.Categorical(
            df["RFID"], categories=sorted_rfids, ordered=True
        )
        return df

    def calculate_sensors_statistics(
        self,
        sensor_name: str,
        frame_values: list[int],
        sensor_values: list[float],
        bin_iterator: list[tuple[int, int]],
    ):
        """Get sensors data (mean, min, max, std, sem) for a bin bordered by
        bin_start_frame and bin_end_frame.

        Returns a list of dicts, one per bin, always matching the number of bins.
        If no data in a bin, fills with np.nan.
        """

        results: list[dict[str, float]] = []
        i_min = 0
        i_max = 0
        for _, f_max in bin_iterator:
            while frame_values[i_max] < f_max:
                i_max += 1
            arr = np.array(sensor_values[i_min : i_max + 1])
            i_min = i_max + 1
            results.append(
                {
                    f"{sensor_name}_MEAN": float(arr.mean()),
                    f"{sensor_name}_MIN": float(arr.min()),
                    f"{sensor_name}_MAX": float(arr.max()),
                    f"{sensor_name}_STD": (
                        float(arr.std()) if len(arr) > 1 else 0.0
                    ),
                    f"{sensor_name}_SEM": (
                        float(arr.std() / np.sqrt(len(arr)))
                        if len(arr) > 1
                        else 0.0
                    ),
                }
            )
        return results

    def get_df_sensors(
        self, bin_iterator: list[tuple[int, int]] | None = None
    ):

        if bin_iterator is None:
            bin_iterator = self.binner.get_bin_iterator()

        query_limits = f" WHERE FRAMENUMBER >= {bin_iterator[0][0]} AND FRAMENUMBER <= {bin_iterator[-1][1]}"

        sensors = [
            "TEMPERATURE",
            "HUMIDITY",
            "SOUND",
            "LIGHTVISIBLE",
            "LIGHTVISIBLEANDIR",
        ]

        cursor = self.animal_pool.conn.cursor()
        cursor.execute(f"SELECT FRAMENUMBER FROM FRAME" + query_limits)
        frame_rows = cursor.fetchall()
        cursor.close()
        frames = [row[0] for row in frame_rows]

        sensors_data: dict[str, list[dict[str, float]]] = {}
        for sensor in sensors:
            print(f"Creating SENSOR dataframe ({sensor})")
            try:
                cursor = self.animal_pool.conn.cursor()
                cursor.execute(f"SELECT {sensor} FROM FRAME" + query_limits)
                values = [row[0] for row in cursor.fetchall()]
                cursor.close()
                sensors_data[sensor] = self.calculate_sensors_statistics(
                    sensor, frames, values, bin_iterator
                )
            except:
                print(f"Cannot access data for {sensor} => Skipping")

        if not sensors_data.keys():
            print("No sensor data available")
            return None
        else:
            for sensor in sensors:
                if sensor not in sensors_data:
                    sensors.remove(sensor)

        results: list[dict[str, Any]] = []
        for i in range(len(bin_iterator)):
            results.append(
                {
                    "START_FRAME": bin_iterator[i][0],
                    "END_FRAME": bin_iterator[i][1],
                    "START_TIME": self.binner.frame_to_time(
                        bin_iterator[i][0]
                    ),
                    "END_TIME": self.binner.frame_to_time(bin_iterator[i][1]),
                }
            )
            for sensor in sensors:
                for key, value in sensors_data[sensor][i].items():
                    results[-1][key] = value

        df = pd.DataFrame(results)
        return df

    def process_sensors(self):
        """Process data between start and end frames to get a DataFrame
        containing sensors data. It will process the whole dataset using
        the process window.
        """
        split_iterator = self.binner.split_iterator_in_chunks(
            self.processing_window, self.binner.get_bin_iterator()
        )
        df = None

        for bin_iterator in split_iterator:
            print(
                f"SENSORS processing for frames {bin_iterator[0][0]} to "
                f"{bin_iterator[-1][1]}"
            )
            processed_df = self.get_df_sensors(bin_iterator=bin_iterator)
            if df is None:
                df = processed_df
            else:
                df = pd.concat([df, processed_df], ignore_index=True)

        if df is None:
            print("Unable to create the sensors dataframe")
            return None

        return df
