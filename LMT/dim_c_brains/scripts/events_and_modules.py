"""
@creation: 26-01-2026
@last update: 28-01-2026
@author: xmousset
"""

from typing import Dict, List, Literal, Optional, Set
from types import ModuleType

from lmtanalysis import (
    BuildEventApproachContact,
    BuildEventApproachRear,
    BuildEventCenterPeripheryLocation,
    BuildEventDetection,
    BuildEventExclusiveCleanOralOralSideSideNoseAnogenitalContact,
    BuildEventExclusiveMoveStopIsolated,
    BuildEventExclusiveUndetected,
    BuildEventFlickering,
    BuildEventFloorSniffing,
    BuildEventFollowZone,
    BuildEventGetAway,
    BuildEventGroup2,
    BuildEventGroup3,
    BuildEventGroup3MakeBreak,
    BuildEventGroup4,
    BuildEventGroup4MakeBreak,
    BuildEventHouse,
    BuildEventHuddling,
    BuildEventInCorner,
    BuildEventLongChase,
    BuildEventMove,
    BuildEventMoveSpeedCategories,
    BuildEventMoveSpeedCategories2,
    BuildEventNest3,
    BuildEventNest4,
    BuildEventObjectSniffingNor,
    BuildEventObjectSniffingNorAcquisitionWithConfig,
    BuildEventObjectSniffingNorTestWithConfig,
    BuildEventOnHouse,
    BuildEventOralGenitalContact,
    BuildEventOralOralContact,
    BuildEventOralSideSequence,
    BuildEventOtherContact,
    BuildEventPassiveAnogenitalSniff,
    BuildEventRear5,
    BuildEventRearCenterPeriphery,
    BuildEventSAP,
    BuildEventSideBySide,
    BuildEventSideBySideOpposite,
    BuildEventSocialApproach,
    BuildEventSocialEscape,
    BuildEventStop,
    BuildEventTrain2,
    BuildEventTrain3,
    BuildEventTrain4,
    BuildEventWallJump,
    BuildEventWaterPoint,
)

ALL_EVENTS: Dict[str, Optional[ModuleType | str]] = {
    "Approach": None,
    "Approach contact": BuildEventApproachContact,
    "Approach rear": BuildEventApproachRear,
    "ASSOCIATION": None,
    "badIdentity": None,
    "badOrientation": None,
    "badSegmentation": None,
    "Behind": None,
    "Break contact": None,
    "Center Zone": BuildEventCenterPeripheryLocation,
    "Contact": None,
    "Corner": BuildEventInCorner,
    "Corner 0": "Corner",
    "Corner 1": "Corner",
    "Corner 2": "Corner",
    "Corner 3": "Corner",
    "coucou": None,
    "Detection": BuildEventDetection,
    "Escape": None,
    "event": None,
    "Flickering": BuildEventFlickering,
    "Floor sniffing": BuildEventFloorSniffing,
    "Follow": None,
    "FollowZone": BuildEventFollowZone,
    "Get away": BuildEventGetAway,
    "Group 3 break": BuildEventGroup3MakeBreak,
    "Group 3 make": "Group 3 break",
    "Group 4 break": BuildEventGroup4MakeBreak,
    "Group 4 make": "Group 4 break",
    "Group2": BuildEventGroup2,
    "Group3": BuildEventGroup3,
    "Group4": BuildEventGroup4,
    "Head detected": None,
    "Huddling": BuildEventHuddling,
    "in house corner": BuildEventHouse,
    "longChase": BuildEventLongChase,
    "Look down": None,
    "MACHINE LEARNING": None,
    "manualContact": None,
    "manualOralGenital": None,
    "manualOralOralContact": None,
    "manualSideSideOpposite": None,
    "manualSideSideSame": None,
    "Move": BuildEventMove,
    "Move high speed": BuildEventMoveSpeedCategories2,
    "Move in contact": "Move",
    "Move isolated": "Move",
    "Nest3_": BuildEventNest3,
    "Nest4_": BuildEventNest4,
    "onHouse": BuildEventOnHouse,
    "Oral-genital Contact": BuildEventOralGenitalContact,
    "Oral-oral Contact": BuildEventOralOralContact,
    "Other contact": BuildEventOtherContact,
    "over house": "in house corner",
    "Passive oral-genital Contact": BuildEventPassiveAnogenitalSniff,
    "Periphery Zone": "Center Zone",
    "Rear at periphery": BuildEventRearCenterPeriphery,
    "Rear in centerWindow": "Rear at periphery",
    "Rear in contact": BuildEventRear5,
    "Rear isolated": "Rear in contact",
    "Rearing": None,
    "RFID ASSIGN ANONY-MOUS TRACK": None,
    "RFID MATCH": None,
    "RFID MISMATCH": None,
    "SAP": BuildEventSAP,
    "seq oral geni - oral oral": "seq oral oral - oral genital",
    "seq oral oral - oral genital": BuildEventOralSideSequence,
    "Side by side Contact": BuildEventSideBySide,
    "Side by side Contact, opposite way": BuildEventSideBySideOpposite,
    "SniffLeft": BuildEventObjectSniffingNor,
    "SniffRight": "SniffLeft",
    "Social approach": BuildEventSocialApproach,
    "Social escape": BuildEventSocialEscape,
    "Stop": None,
    "Stop in contact": BuildEventStop,
    "Stop isolated": BuildEventStop,
    "Train2": BuildEventTrain2,
    "Train3": BuildEventTrain3,
    "Train4": BuildEventTrain4,
    "WallJump": BuildEventWallJump,
    "Water Stop": BuildEventWaterPoint,
    "Water Zone": "Water Stop",
}


def get_module(event_name: str):
    """
    Retrieve the module object associated with a given event name.

    This function looks up the provided event name in the ALL_EVENTS mapping.
    If the mapping returns a string, it recursively resolves the actual module.
    If the event name is not found or the module is not implemented,
    returns None.

    Args:
        event_name (str): The name of the event to look up.
    Returns:
        (ModuleType | None): The module object associated with the event name,
        or None if no corresponding module is found or implemented.
    Raises:
        AssertionError: If the resolved module is not None or a ModuleType instance.
    """
    module = ALL_EVENTS.get(event_name)
    if isinstance(module, str):
        module = get_module(module)
    assert module is None or isinstance(module, ModuleType)
    return module


def get_modules(events: list[str] | set[str]):
    """Get a set of unique modules associated with a list of event names."""
    modules_set: set[ModuleType] = set()

    if isinstance(events, list):
        events = set(events)

    for event in events:
        module = get_module(event)
        if module is not None:
            modules_set.add(module)
    return modules_set
