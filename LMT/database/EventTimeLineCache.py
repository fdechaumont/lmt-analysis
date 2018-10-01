'''
Created on 25 sept. 2018

@author: Fab
'''
from database.Event import EventTimeLine

eventCacheDico_={}
    
def getEventTimeLineCached( connection, file, eventName, idA=None, idB=None, idC=None, idD = None, minFrame=None, maxFrame=None ):
    
    global eventCacheDico_
    
    if (file, eventName, idA, idB, idC, idD, minFrame, maxFrame) in eventCacheDico_: 
        eventTimeLine = eventCacheDico_[ file, eventName, idA, idB, idC, idD, minFrame, maxFrame ]
        print ( eventName , " Id(",idA ,",", idB, ",", idC, "," , idD , ") Loaded from cache (" , len( eventTimeLine.eventList ) , " records. )")
        return eventTimeLine

    eventTimeLine = EventTimeLine( connection, eventName , idA, idB, idC, idD, minFrame, maxFrame )
    eventCacheDico_[ file, eventName, idA, idB, idC, idD, minFrame, maxFrame ] = eventTimeLine
    print ( "Caching eventTimeLine")
    return eventTimeLine
        
def flushEventTimeLineCache(self):
    eventCacheDico_.clear()