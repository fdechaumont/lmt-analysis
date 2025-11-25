"""
Created on 25-11-2025
@author: Xavier Mousset
"""
from typing import Any
import sqlite3
from time import *

from lmtanalysis.Animal import *
from lmtanalysis.Detection import *
from lmtanalysis.Measure import *
import matplotlib.pyplot as plt
import numpy as np
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis.Chronometer import Chronometer
from lmtanalysis.TaskLogger import TaskLogger


def flush(connection):
    """Flush "flickering" event in database"""
    deleteEventTimeLineInBase(connection, "flickering")


def reBuildEvent(
    connection: sqlite3.Connection,
    file: Any,
    tmin : int|None = None,
    tmax : int|None = None,
    pool: AnimalPool|None = None,
    animalType: Any = None,
    ):
    """
    Rebuilds the "flickering" events for all animals in the database within a
    specified time window.

    Flickering is calculated on the last 30 frames if available (equal to one
    second) and with at least 6 frames.
    Loads animal detections, computes local velocities and global displacements
    over a rolling window, detects "flickering" events based on movement
    criteria. Results are stored in the database as events.

    Parameters
    ----------
    connection : sqlite3.Connection
        The SQLite database connection.
    file : Any
        The file path or object (not used directly in this function).
    tmin : int or None
        The start time for loading detections (frame or timestamp).
    tmax : int or None
        The end time for loading detections (frame or timestamp).
    pool : AnimalPool or None
        Optional existing AnimalPool instance (create new one if None).
    animalType : Any
        Optional animal type filter (not used).

    Returns
    -------
    None
    """
    
    if pool is None:
        pool = AnimalPool()
        pool.loadAnimals(connection)
        pool.loadDetection(start= tmin, end= tmax)
    
    window = 30  # window size in frames
    
    for animal_key in pool.animalDictionary.keys():
        
        eventName = "flickering"
        print(eventName)
        
        flickeringTimeLine = EventTimeLine(
            None, eventName, animal_key, None, None, None, loadEvent= False
        )
        
        animal = pool.animalDictionary[animal_key]
        list_frames = sorted(animal.detectionDictionary.keys())
        if list_frames == []:
            continue
        
        result = {}
        list_vx = [0]
        list_vy = [0]
        previous_f = list_frames[0]

        for idx, f in enumerate(list_frames[1:]):
            frame_gap = f - previous_f
            
            # compute speed
            data = animal.detectionDictionary.get(f)
            previous_data = animal.detectionDictionary.get(previous_f)
            vx = (data.massX - previous_data.massX) / frame_gap
            vy = (data.massY - previous_data.massY) / frame_gap
            
            list_vx.append(vx)
            list_vy.append(vy)

            previous_f = f
            
            if len(list_vx) < window:
                continue
            
            # ensure to take only frames from the last 30 frames (1 second)
            local_window = 0
            for local_window in range(window, 2, -1):
                if list_frames[idx-local_window] >= list_frames[idx]-window+1:
                    break
            
            # keep at least 6 frames to have some statistics
            if local_window < 6:
                continue
            
            array_vx = np.array(list_vx[-window:])
            array_vy = np.array(list_vy[-window:])
            
            mean_speed = np.mean(array_vx**2 + array_vy**2)
            global_displacement = np.mean(array_vx)**2 + np.mean(array_vy)**2

            if mean_speed > 5 and mean_speed > 10*global_displacement:
                result[f] = True
        
        flickeringTimeLine.reBuildWithDictionary(result)
        flickeringTimeLine.endRebuildEventTimeLine(connection)
    
    # log process
    t = TaskLogger(connection)
    if tmin is None or tmax is None:
        t.addLog("Build Event Flickering (tmin or tmax is None)")
    else:
        t.addLog("Build Event Flickering", tmin= tmin, tmax= tmax)
    print("Rebuild event finished.")
