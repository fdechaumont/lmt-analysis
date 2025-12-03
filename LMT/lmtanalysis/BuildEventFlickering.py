"""
Created on 25-11-2025
@author: Xavier Mousset
"""
import sqlite3
import numpy as np
from typing import Any

from lmtanalysis.Animal import AnimalPool, EventTimeLine
from lmtanalysis.Event import deleteEventTimeLineInBase
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
    window: int = 19,
    few_frames_default_value: bool = False,
    ):
    """
    Rebuilds the "flickering" events for all animals in the database within a
    specified time window.

    Flickering is calculated on 19 frames (centered window, equal to 0.6
    second) and with at least 7 frames (0.2 second).

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
    window : int, optional
        The size of the rolling window (in frames) used to compute flickering
        events. Must be at least 7. Default is 19 (0.6 second).
    few_frames_default_value : bool, optional
        Define if it is a flickering or not when there are not enough frames
        available (<7) for flickering calculation. Default is False, so not a
        flickering event.

    Returns
    -------
    None
    """
    
    if pool is None:
        pool = AnimalPool()
        pool.loadAnimals(connection)
        pool.loadDetection(start= tmin, end= tmax)
    
    if window < 7:
        raise ValueError("Minimum window size for flickering is 7 frames.")
    
    half_w = window // 2
    left_w = half_w
    right_w = half_w
    if window % 2 == 0:
        right_w = right_w - 1
    
    data = {}
    
    for animal_key in pool.animalDictionary.keys():
        eventName = "flickering"
        
        flickeringTimeLine = EventTimeLine(
            None, eventName, animal_key, None, None, None, loadEvent= False
        )
        
        animal = pool.animalDictionary[animal_key]
        animal_frames = sorted(animal.detectionDictionary.keys())
        if animal_frames == []:
            continue
        
        # compute speed and acceleration
        vx = [0.]
        vy = [0.]
        previous_f = animal_frames[0]
        for f in animal_frames[1:]:
            frame_gap = f - previous_f
            detected_data = animal.detectionDictionary.get(f)
            previous_data = animal.detectionDictionary.get(previous_f)
            vx.append((detected_data.massX - previous_data.massX) / frame_gap)
            vy.append((detected_data.massY - previous_data.massY) / frame_gap)
            previous_f = f
        
        # detect flickering
        result = {}
        for idx, f in enumerate(animal_frames[left_w: -right_w], start= left_w):
            
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
            if local_lw + local_rw < 6:
                if few_frames_default_value:
                    result[f] = True
                continue
            
            start = idx - local_lw
            end = idx + local_rw
            array_vx = np.array(vx[start : end])
            array_vy = np.array(vy[start : end])
            
            speed = array_vx**2 + array_vy**2
            max_speed = np.max(speed)
            mean_speed = np.mean(speed)
            real_speed = np.mean(array_vx)**2 + np.mean(array_vy)**2

            # flickering detection criteria
            # 70 (px/frame)² ~ 1.5 cm/frame
            # 16 (px/frame)² ~ 0.70 cm/frame
            if max_speed > 70 and mean_speed - real_speed > 16:
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
