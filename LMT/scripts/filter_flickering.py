"""
Created on 24-11-2025
@author: Xavier Mousset
"""

import math

from lmtanalysis.Animal import *


def get_flickering_frames(
    connection : sqlite3.Connection,
    animal : Animal,
    ) -> dict[int, bool]:
    """
    Returns a dictionary with frame numbers as keys corresponding to a
    flickering events of `animal`.
    """
    flicker_time_line = EventTimeLine(connection, "flickering", animal.baseId)
    flicker_frames = flicker_time_line.getDictionary()
    return flicker_frames


def get_distance(
    connection : sqlite3.Connection,
    animal : Animal,
    f_min : int = 0,
    f_max : int|None = None,
    ) -> float:
    """
    Returns the distance traveled by `animal` (in cm) between `f_min` and
    `f_max`. By default, the distance is computed until the last detection of
    the animal. This function filters out all frames where there is a
    flickering event.
    """
    
    print(
        f"Computing distance for animal {animal.baseId} "
        f"from {f_min} to {f_max}."
    )
    
    # get f_max if not provided
    if f_max is None:
        f_max = animal.getMaxDetectionT()
    
    # check validity of f_min and f_max
    if f_max is None or f_max <= f_min:
        return 0.
    
    # get all flickering frames
    flicker_frames = get_flickering_frames(connection, animal)
    
    previous_is_flicker_frame = False
    distance = 0.
    for f in range(f_min+1, f_max):
        
        if previous_is_flicker_frame:
            previous_is_flicker_frame = False
            continue
        
        previous_pos = animal.detectionDictionary.get(f-1)
        current_pos = animal.detectionDictionary.get(f)

        if current_pos is None or previous_pos is None:
            continue
        
        if f in flicker_frames:
            previous_is_flicker_frame = True
            continue
        
        iterative_distance = math.hypot(
            current_pos.massX-previous_pos.massX,
            current_pos.massY-previous_pos.massY
        )
        
        # discard if distance between 2 frames is too large
        if iterative_distance > 85.5:
            continue
        
        distance += iterative_distance

    # convert to cm
    distance *= animal.parameters.scaleFactor # type: ignore

    return distance