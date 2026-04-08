"""
Created on 25-11-2025
@author: Xavier Mousset
"""

from re import match
import sqlite3
import numpy as np
from typing import Any

from lmtanalysis.Animal import AnimalPool, AnimalType, EventTimeLine
from lmtanalysis.Event import deleteEventTimeLineInBase
from lmtanalysis.TaskLogger import TaskLogger


# name of the event to build (should correspond to the file name)
EVENT_NAME = "Flickering"


# DO NOT MODIFY THIS PART, UNLESS YOU KNOW WHAT YOU ARE DOING
def flush(connection):
    """Flush event in database"""
    deleteEventTimeLineInBase(connection, EVENT_NAME)


def reBuildEvent(
    connection: sqlite3.Connection,
    file: Any | None = None,
    tmin: int | None = None,
    tmax: int | None = None,
    pool: AnimalPool | None = None,
    animalType: AnimalType | None = AnimalType.MOUSE,
    window: int = 19,
    event_min_frames: int = 6,
    flick_when_few_frames: bool = False,
):
    """
    Rebuilds the 'Flickering' events for all animals in the database within a
    specified time window.

    Flickering is calculated on 19 frames (centered window, equal to 0.6
    second) and with at least 7 frames (0.2 second).

    Parameters
    ----------
    connection : sqlite3.Connection
        The SQLite database connection.
    file : Any or None, optional
        The file path or object. (not used here)
        Can be used by EventTimeLineCached to cache event loading.
        Default is None.
    tmin : int or None, optional
        The start time for loading detections in frame. If None, it will load
        all detections from the start.
    tmax : int or None, optional
        The end time for loading detections in frame. If None, it will load
        all detections until the end.
    pool : AnimalPool or None, optional
        Optional existing AnimalPool instance (create new one if None).
    animalType : AnimalType or None, optional
        The appropriate animal type. Default is MOUSE.
    window : int, optional
        The size of the rolling window (in frames) used to compute flickering
        events. Must be at least 7. Default is 19 (0.6 second).
    event_min_frames : int, optional
        The minimum number of frames required to consider a flickering event.
        Default is 6.
    flick_when_few_frames : bool, optional
        When the minimum number of frames is not reached (< event_min_frames),
        define if it must be considered as a flickering or not. Default is
        False (i.e., small numbers of frames are not considered a flickering
        event).

    Returns
    -------
    None
    """

    # Inputs errors
    # ----------------
    if window < 7:
        raise ValueError("Minimum window size for flickering is 7 frames.")

    # DO NOT MODIFY
    # ----------------
    if pool is None:
        pool = AnimalPool()
        pool.loadAnimals(connection)
        pool.loadDetection(start=tmin, end=tmax)

    # Flickering Criteria
    # ----------------
    match animalType:
        case AnimalType.MOUSE:
            # 81 (px/frame)² = 9 px/frame ~ 1.6 cm/frame minimum max_speed
            # 16 (px/frame)² = 4 px/frame ~ 0.70 cm/frame min speed difference
            criteria = {
                "min_speed": 81,
                "speed_displacement_diff": 16,
            }
        case AnimalType.RAT:
            # 81 (px/frame)² = 9 px/frame ~ 1.6 cm/frame minimum max_speed
            # 16 (px/frame)² = 4 px/frame ~ 0.70 cm/frame min speed difference
            criteria = {
                "min_speed": 81,
                "speed_displacement_diff": 16,
            }
        case _:
            raise ValueError("Animal type not supported for flickering event.")

    half_w = window // 2
    left_w = half_w
    right_w = half_w
    if window % 2 == 0:
        right_w = right_w - 1

    for animal_key in pool.animalDictionary.keys():

        flickeringTimeLine = EventTimeLine(
            conn=connection,
            eventName=EVENT_NAME,
            idA=animal_key,
            idB=None,
            idC=None,
            idD=None,
            loadEvent=False,
            minFrame=tmin,
            maxFrame=tmax,
        )

        result = {}

        animal = pool.animalDictionary[animal_key]

        # ================ Flickering logic ================

        animal_frames = np.array(sorted(animal.detectionDictionary.keys()))
        if animal_frames.size == 0:
            continue

        # compute speed and acceleration
        frame_gaps = np.diff(animal_frames)
        massX = np.array(
            [animal.detectionDictionary.get(f).massX for f in animal_frames]
        )
        massY = np.array(
            [animal.detectionDictionary.get(f).massY for f in animal_frames]
        )

        vx = np.zeros_like(massX)
        vy = np.zeros_like(massY)
        vx[1:] = np.diff(massX) / frame_gaps
        vy[1:] = np.diff(massY) / frame_gaps

        # detect flickering
        for idx, f in enumerate(animal_frames[left_w:-right_w], start=left_w):
            f_key = int(f)

            # ensure to not take big frame gaps
            local_lw = left_w
            local_rw = right_w
            frame_ref = animal_frames[idx]
            while (
                local_lw > 0
                and animal_frames[idx - local_lw] < frame_ref - left_w
            ):
                local_lw -= 1
            while (
                local_rw > 0
                and animal_frames[idx + local_rw] > frame_ref + right_w
            ):
                local_rw -= 1

            # minimum number of frames required
            if local_lw + local_rw < event_min_frames:
                if flick_when_few_frames:
                    result[f_key] = True
                continue

            start = idx - local_lw
            end = idx + local_rw
            local_vx = vx[start : end + 1]
            local_vy = vy[start : end + 1]

            speed = local_vx**2 + local_vy**2
            max_speed = np.max(speed)
            mean_speed = np.mean(speed)
            displacement = np.mean(local_vx) ** 2 + np.mean(local_vy) ** 2

            # criteria for flickering
            if (
                max_speed > criteria["min_speed"]
                and mean_speed - displacement
                > criteria["speed_displacement_diff"]
            ):
                result[f_key] = True

        # ================ End of Flickering logic ================

        # DO NOT MODIFY
        # ----------------
        flickeringTimeLine.reBuildWithDictionary(result)
        flickeringTimeLine.endRebuildEventTimeLine(connection)

    # DO NOT MODIFY
    # ----------------
    # log process for debugging and record keeping
    t = TaskLogger(connection)
    if tmin is None or tmax is None:
        t.addLog("Build Event Flickering (tmin or tmax is None)")
    else:
        t.addLog("Build Event Flickering", tmin=tmin, tmax=tmax)
    print("Rebuild event finished.")
