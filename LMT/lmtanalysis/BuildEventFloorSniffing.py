"""
Created on 10-02-2026
@author: Xavier Mousset
"""

import sqlite3
import numpy as np
from typing import Any


from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.Animal import AnimalPool, AnimalType, EventTimeLine
from lmtanalysis.Event import deleteEventTimeLineInBase
from lmtanalysis.TaskLogger import TaskLogger
from lmtanalysis.Detection import Detection


# name of the event to build (should correspond to the file name)
EVENT_NAME = "Floor sniffing"


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
    window: int = 45,
):
    """
    Rebuilds the appropriate event for all animals in the database.

    Parameters
    ----------
    connection : sqlite3.Connection
        The SQLite database connection.
    file : Any or None, optional
        The file path or object.
        Can be used by EventTimeLineCached to cache event loading.
        Default is None.
    tmin : int or None, optional
        Start time for detections (in frame).
    tmax : int or None, optional
        End time for detections (in frame).
    pool : AnimalPool or None, optional
        AnimalPool instance (create new one if None using tmin and tmax).
    animalType : AnimalType or None, optional
        The appropriate animal type. Default is MOUSE.
    window: int, optional
        The time window for event detection (in frames).
        Default is 45 (1.5 second at 30 fps).
        This parameter can be used to adjust the time window for event
        detection, depending on the expected duration of the event.

    Returns
    -------
    None
    """

    # DO NOT MODIFY THIS PART, UNLESS YOU KNOW WHAT YOU ARE DOING
    if pool is None:
        pool = AnimalPool()
        pool.loadAnimals(connection)
        pool.loadDetection(start=tmin, end=tmax)

    # Detection parameters and threshholds
    MIN_STOP_DURATION = 60  # 2 seconds at 30 fps
    BODY_SLOPE_MIN = -25
    BODY_SLOPE_MAX = -15

    for animal_key in pool.animalDictionary.keys():

        # create a new event timeline for each animal
        # it will be filled with the result of your event detection
        # then saved in database at the end of the process
        your_event_TimeLine = EventTimeLine(
            conn=None,
            eventName=EVENT_NAME,
            idA=animal_key,
            idB=None,
            idC=None,
            idD=None,
            loadEvent=False,
        )

        # prepare a dictionary to store the result of your event detection
        # the key of the dictionary should be the frame of the event occurrence
        result = {}

        # example of how to store event detection in results:
        # result[f] = True
        # this means your event occur at frame "f"
        # NEVER add a "False" value to the dictionary

        # get the animal object from the pool with the animal key (id)
        animal = pool.animalDictionary[animal_key]

        #######################################
        #   YOUR CODE HERE   #
        #######################################

        stop_frames = EventTimeLine(
            conn=connection,
            eventName="Stop",
            idA=animal_key,
        ).getDictionary()

        animal_frames = np.array(sorted(animal.detectionDictionary.keys()))

        half_w = window // 2
        left_w = half_w
        right_w = half_w
        if window % 2 == 0:
            right_w = right_w - 1

        for f_str in animal_frames:
            f_int = int(f_str)

            # OPTION 1
            frame_result = check_body_slope(
                animal.detectionDictionary.get(f_str)
            )
            if not frame_result:
                continue

            # OPTION 2
            if f_str not in stop_frames:
                continue
            frame_result = check_body_size(
                animal.detectionDictionary.get(f_str)
            )
            if not frame_result:
                continue
            frame_result = check_head_movement(
                animal,
                f_str,
                window,
            )
            if not frame_result:
                continue

            result[f_str] = True

        #######################################
        #   END OF YOUR CODE   #
        #######################################

        # DO NOT MODIFY THIS PART, UNLESS YOU KNOW WHAT YOU ARE DOING
        # store your result in the event timeline and save it in database
        your_event_TimeLine.reBuildWithDictionary(result)
        your_event_TimeLine.endRebuildEventTimeLine(connection)

    # DO NOT MODIFY THIS PART, UNLESS YOU KNOW WHAT YOU ARE DOING
    # log process for debugging and record keeping
    f_str = TaskLogger(connection)
    if tmin is None or tmax is None:
        f_str.addLog(f"Build Event {EVENT_NAME} (tmin or tmax is None)")
    else:
        f_str.addLog(f"Build Event {EVENT_NAME}", tmin=tmin, tmax=tmax)
    print(f"Rebuild {EVENT_NAME} event finished.")


def check_body_slope(detection: Detection):
    """
    Compute the body slope angle (in degrees) from a Detection object.
    Uses frontX, frontY, frontZ and backX, backY, backZ.
    The slope is the angle in the vertical plane:
        atan2(frontZ - backZ, horizontal_distance_front_to_back)
    A negative slope means the front (nose) is lower than the back,
    indicating the animal is tilting its head downward towards the floor.
    Returns None if coordinates are missing.
    """
    if detection is None:
        return False
    if (
        detection.frontX is None
        or detection.frontY is None
        or detection.frontZ is None
        or detection.backX is None
        or detection.backY is None
        or detection.backZ is None
    ):
        return False

    body_length = np.hypot(
        detection.frontX - detection.backX, detection.frontY - detection.backY
    )

    if body_length <= 0:
        return False

    height = detection.frontZ - detection.backZ
    slope = np.atan2(height, body_length)

    if slope >= -5 * np.pi / 36 and slope <= -3 * np.pi / 36:
        return True
    return False


def check_body_size(
    detection: Detection,
):
    """
    Check if the animal is small.
    This can be used as an additional criterion for floor sniffing detection.
    Returns True if the animal is small, False otherwise.
    """

    criteria = {
        "length_limit": 10,  # need adjustements
    }

    if detection is None:
        return False
    if (
        detection.frontX is None
        or detection.frontY is None
        or detection.frontZ is None
        or detection.backX is None
        or detection.backY is None
        or detection.backZ is None
    ):
        return False

    body_length = np.hypot(
        detection.frontX - detection.backX, detection.frontY - detection.backY
    )

    if body_length <= 0:
        return False

    if body_length > criteria["length_limit"]:
        return False

    return True


def check_head_movement(
    animal: Any,
    frame: int,
    window: int,
):
    """
    Check if the animal is moving its head.
    This can be used as an additional criterion for floor sniffing detection.
    Returns True if the animal is moving its head, False otherwise.
    """

    criteria = {
        "min_cumul_speed": 5,  # need adjustements
        "max_displacement": 1,  # need adjustements
    }

    local_vx = []
    local_vy = []

    half_w = window // 2
    left_w = half_w
    right_w = half_w
    if window % 2 == 0:
        right_w = right_w - 1

    head_x = []
    head_y = []
    for f in range(frame - left_w, frame + right_w):
        detection = animal.detectionDictionary.get(f)
        if detection is None:
            continue
        if detection.frontX is None or detection.frontY is None:
            continue
        head_x.append(detection.frontX)
        head_y.append(detection.frontY)

    if len(head_x) < 40:
        return False

    head_x = np.array(head_x)
    head_y = np.array(head_y)

    head_vx = np.diff(head_x)
    head_vy = np.diff(head_y)

    head_cumul_speed = np.sum(head_vx**2 + head_vy**2)
    if head_cumul_speed < criteria["min_speed"]:
        return False

    head_displacement = np.mean(head_vx) ** 2 + np.mean(head_vy) ** 2
    if head_displacement > criteria["max_displacement"]:
        return False

    return True
