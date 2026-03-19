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


# EVENT NAME (should correspond to the file name)
# ----------------
EVENT_NAME = "Your_event"


# DO NOT MODIFY
# ----------------
def flush(connection):
    """Flush event in database"""
    deleteEventTimeLineInBase(connection, EVENT_NAME)


# YOUR EVENT
# ----------------
def reBuildEvent(
    connection: sqlite3.Connection,
    file: Any | None = None,
    tmin: int | None = None,
    tmax: int | None = None,
    pool: AnimalPool | None = None,
    animalType: AnimalType | None = None,
    # your variables here
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
        Start time for detections (in frame). If None, it will load all
        detections from the start.
    tmax : int or None, optional
        End time for detections (in frame). If None, it will load all
        detections until the end.
    pool : AnimalPool or None, optional
        AnimalPool instance (create new one if None using tmin and tmax).
    animalType : AnimalType or None, optional
        The appropriate animal type. Default is MOUSE.
    YOUR VARIABLES : type
        Description of your variables here.

    Returns
    -------
    None
    """

    # DO NOT MODIFY
    # ----------------
    if pool is None:
        pool = AnimalPool()
        pool.loadAnimals(connection)
        pool.loadDetection(start=tmin, end=tmax)

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
            minFrame=tmin,
            maxFrame=tmax,
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

        # ================ YOUR CODE HERE ================

        # example of how to get the frames of the animal detections
        animal_frames = np.array(sorted(animal.detectionDictionary.keys()))

        # example of how to get the massX position of the animal detections
        massX = np.array(
            [animal.detectionDictionary.get(f).massX for f in animal_frames]
        )

        if animal_frames.size == 0:
            continue

        # example of how to compute speed
        frame_gaps = np.diff(animal_frames)
        vx = np.zeros_like(massX)
        vx[1:] = np.diff(massX) / frame_gaps

        # example of how to get the frames corresponding to an existing event
        stop_frames = EventTimeLine(
            conn=connection,
            eventName="Stop",
            idA=animal_key,
        ).getDictionary()

        # ================ END OF YOUR CODE ================

        # DO NOT MODIFY
        # ----------------
        # store your result in the event timeline and save it in database
        your_event_TimeLine.reBuildWithDictionary(result)
        your_event_TimeLine.endRebuildEventTimeLine(connection)

    # DO NOT MODIFY
    # ----------------
    # log process for debugging and record keeping
    t = TaskLogger(connection)
    if tmin is None or tmax is None:
        t.addLog(f"Build Event {EVENT_NAME} (tmin or tmax is None)")
    else:
        t.addLog(f"Build Event {EVENT_NAME}", tmin=tmin, tmax=tmax)
    print(f"Rebuild {EVENT_NAME} event finished.")
