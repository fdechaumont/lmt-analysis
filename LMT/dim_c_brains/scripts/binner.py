"""
@author: xmousset
"""

from sqlite3 import Connection
import pandas as pd
from typing import Any, Dict, List, Literal


class Binner:
    """Utility class design to manage the binning with frame numbers for LMT
    experiment.
    It cannot manage bins smaller than OneMinute.
    All bin size must be at least 1."""

    @staticmethod
    def get_last_frame(connection: Connection):
        """Get the last FRAMENUMBER and TIMESTAMP from LMT FRAME table. Useful
        to initialize the Binner with the correct time reference."""
        query = "SELECT FRAMENUMBER, TIMESTAMP FROM FRAME ORDER BY FRAMENUMBER DESC LIMIT 1"
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()

        if not result:
            raise ValueError("No data found in FRAME table")

        last_FRAMENUMBER = result[0]
        last_TIMESTAMP = result[1]

        if not (isinstance(last_FRAMENUMBER, int)) or not (
            isinstance(last_TIMESTAMP, int)
        ):
            raise ValueError("Invalid type of data found in FRAME table")

        return last_FRAMENUMBER, last_TIMESTAMP

    def __init__(
        self,
        last_frame: int,
        last_timestamp: int,
        bin_size: int | pd.Timedelta = 15 * 60 * 30,  # 15 minutes at 30 FPS
        start: int | pd.Timestamp | None = None,
        end: int | pd.Timestamp | None = None,
        fps: int = 30,  # frames per second
        UTC_offset: float = 1.0,
    ):
        """
        Initialize Binner with last FRAMENUMBER and TIMESTAMP of a
        SQLite database produce by LMT experiment.

        Args:
            last_frame (int): last FRAMENUMBER value in LMT FRAME table.
            last_timestamp (int): TIMESTAMP value of 'last_frame' (in *ms*).
            bin_size (int | pd.Timedelta | None): binning value (in *frames* or
                *timedelta*). Default to *15 min* at *30 FPS*.
            start (int | pd.Timestamp | None): starting frame number or
                timestamp for binning.
            end (int | pd.Timestamp | None): ending frame number or timestamp
                for binning.
            fps (int, optional): frames per second of the experiment. Defaults
                to *30*.
            UTC_offset (float, optional): UTC offset in hours for correct
                timezone conversion (e.g. *+9.0* for Tokyo). Defaults to *1.0*.

        Note that the UTC offset is only used for the conversion of frame
        numbers to timestamps and vice versa, and does not affect the actual
        binning process.
        """
        self.last_frame = last_frame
        self.last_timestamp = last_timestamp
        self.UTC_offset = pd.Timedelta(hours=UTC_offset)
        self.set_parameters(bin_size, start, end, fps)

        print(f"Binner initialized with:")
        print(f"last FRAMENUMBER: {self.last_frame}")
        print(f"last TIMESTAMP: {self.last_timestamp}")
        print(f"Experiment started at {self.frame_to_time(1)}")

    def frame_to_time(self, framenumber: int) -> pd.Timestamp:
        """Convert a frame number to a pandas Timestamp."""
        time_delta = pd.to_timedelta(framenumber / self.fps, unit="s")
        return self.time_0 + time_delta

    def time_to_frame(self, time: pd.Timestamp) -> int:
        """Convert a pandas Timestamp to a frame number."""
        time_delta = time - self.time_0
        return round(time_delta.total_seconds() * self.fps)

    def timedelta_to_frames(self, delta: pd.Timedelta) -> int:
        """Convert a pandas Timedelta to number of frames."""
        return round(delta.total_seconds() * self.fps)

    def frames_to_timedelta(self, frames: int) -> pd.Timedelta:
        """Convert number of frames to a pandas Timedelta."""
        return pd.Timedelta(seconds=frames / self.fps)

    def set_parameters(
        self,
        bin_size: int | pd.Timedelta | None = None,
        start: int | pd.Timestamp | None = None,
        end: int | pd.Timestamp | None = None,
        fps: int | None = None,
    ):
        """Set bin size (in *frames*), frame limits (in *frames*), and FPS
        (*frames/second*) and save the reference bin (bin_0).
        Also initialize the reference time (time_0) that correspond to bin_0
        with appropriate timezone offset and the bin dataframe (bin_df).
        """
        if fps is not None:
            if fps < 1:
                raise ValueError("FPS must be at least 1")
            self.fps = fps

        timestamp_0 = self.last_timestamp - (self.last_frame / self.fps * 1000)
        self.bin_0: Dict[str, Any] = {
            "FRAMENUMBER": 0,
            "TIMESTAMP": timestamp_0 + self.UTC_offset.total_seconds() * 1000,
        }
        self.time_0 = pd.to_datetime(timestamp_0, unit="ms") + self.UTC_offset

        if isinstance(bin_size, pd.Timedelta):
            bin_size = self.timedelta_to_frames(bin_size)

        if bin_size is not None:
            if bin_size < 1:
                raise ValueError("bin_size must be at least 1 frame")
            self.bin_size = bin_size

        if isinstance(start, pd.Timestamp):
            start = self.time_to_frame(start)
        if start is None or start < 1:
            self.start_frame = 1
        elif start > self.last_frame:
            raise ValueError(
                f"start_frame out of range (start_frame = {start} "
                f"> last_frame = {self.last_frame})"
            )
        else:
            self.start_frame = start

        if isinstance(end, pd.Timestamp):
            end = self.time_to_frame(end)
        if end is None or end > self.last_frame:
            self.end_frame = self.last_frame
        elif end < 1:
            raise ValueError(f"end_frame out of range (end_frame = {end} < 1)")
        else:
            self.end_frame = end

        if self.start_frame >= self.end_frame:
            raise ValueError(
                f"Invalid frame limits (start_frame = {self.start_frame} >= "
                f"end_frame = {self.end_frame})"
            )

        self.calculate_bin_df()

    def calculate_bin_df(self):
        """Calculate the bin dataframe with START_FRAME, END_FRAME, START_TIME,
        and END_TIME as columns."""

        # get the first bin starting frame number
        # it is a negative value because bins start at round hours
        dt_0 = self.frame_to_time(self.bin_size)
        dt_bin_0 = dt_0.floor(f"{self.bin_size // (60 * self.fps)}min")
        start_frame_bin_1 = self.time_to_frame(dt_bin_0)

        # calculate starting frame of each bins until last frame
        bin_start_frames: List[int] = []
        f = start_frame_bin_1 - self.bin_size
        while f < self.last_frame:
            bin_start_frames.append(f)
            f += self.bin_size

        # create the dataframe with all bin information
        list_df = []
        for f in bin_start_frames:
            start_frame = f if f > 0 else 1
            end_frame = (
                f + self.bin_size - 1
                if f <= self.last_frame
                else self.last_frame
            )
            list_df.append(
                {
                    "START_FRAME": start_frame,
                    "END_FRAME": end_frame,
                    "START_TIME": self.frame_to_time(f),
                    "END_TIME": self.frame_to_time(f + self.bin_size - 1),
                }
            )

        self.bin_df = pd.DataFrame(list_df)
        return self.bin_df

    def get_bin_list(
        self,
        bin_edge: Literal["START", "END"],
        unit: Literal["FRAME", "TIME"] = "FRAME",
    ):
        """
        Get a list of bin edges (frame numbers or timestamps) between
        start_frame and end_frame.

        Parameters
        ----------
        bin_edge : {'START', 'END'}
            Whether to return the start or end of each bin.
        unit : {'FRAME', 'TIME'}, optional
            Whether to return frame numbers ('FRAME') or timestamps ('TIME').
            Default is 'FRAME'.

        Returns
        -------
        list of int or list of pandas.Timestamp
            List of bin edges (either frame numbers or timestamps) within the
            specified range.

        Examples
        --------
        Suppose self.bin_df contains:

        >>> # START_FRAME  END_FRAME  START_TIME           END_TIME
        >>> # 1            12_999      2026-01-01 00:00:00  2026-01-01 00:14:59
        >>> # 13_000       39_999      2026-01-01 00:15:00  2026-01-01 00:29:59
        >>> # 40_000       56_999      2026-01-01 00:30:00  2026-01-01 00:44:59

        The following code would yield:
        >>> # if start_frame is None and end_frame is None :
        >>> DatetimeBinner.get_bin_list('END')
        [12_999, 39_999, 56_999, ...]

        >>> # if start_frame is 5_000 and end_frame is 25_000 :
        >>> DatetimeBinner.get_bin_list('START', unit='TIME')
        [Timestamp('2026-01-01 00:00:00'), Timestamp('2026-01-01 00:15:00')]
        """

        mask = (self.bin_df["END_FRAME"] >= self.start_frame) & (
            self.bin_df["START_FRAME"] <= self.end_frame
        )

        return self.bin_df[f"{bin_edge}_{unit}"].loc[mask].tolist()

    def get_bin_iterator(self):
        """Get a bin iterator (list of (start, end) tuples) between
        'self.start_frame' and 'self.end_frame'.
        """

        frames_start = self.get_bin_list("START")
        frames_end = self.get_bin_list("END")

        if frames_start[0] < self.start_frame:
            frames_start[0] = self.start_frame

        if frames_end[-1] > self.end_frame:
            frames_end[-1] = self.end_frame

        bin_iterator: List[tuple[int, int]] = []
        for start, end in zip(frames_start, frames_end):
            if end > self.start_frame and start < self.end_frame:
                if start < self.start_frame:
                    start = self.start_frame
                if end > self.end_frame:
                    end = self.end_frame
                bin_iterator.append((start, end))

        return bin_iterator

    def split_iterator_in_chunks(
        self,
        chunk_size: int | pd.Timedelta,
        bin_iterator: List[tuple[int, int]],
    ):
        """Split the given bin iterator (list of (start, end) tuples), in
        chunks of chunk_size (in *frames* or *timedelta*). Useful to split the
        processing of bins in smaller chunks for memory usage reduction.
        """

        if isinstance(chunk_size, pd.Timedelta):
            chunk_size = self.timedelta_to_frames(chunk_size)

        chunked_iterator: List[List[tuple[int, int]]] = [
            [bin_iterator[0]],
        ]
        chunk_start = bin_iterator[0][0]

        for bin in bin_iterator[1:]:
            if bin[1] - chunk_start + 1 < chunk_size:
                chunked_iterator[-1].append(bin)
            else:
                chunked_iterator.append([bin])
                chunk_start = bin[0]

        return chunked_iterator
