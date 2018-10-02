'''
Created on 25 sept. 2018

@author: Fab
'''
from database.Event import EventTimeLine

eventCacheDico_={}
eventCacheEnable_ = True

def disableEventTimeLineCache():
    ''' If you are using a computer with small amount of RAM, it might be better to disable cache '''
    eventCacheDico_.clear()
    global eventCacheEnable_
    eventCacheEnable_ = False
    print( "Cache event is disabled" )
    
    
def EventTimeLineCached( connection, file, eventName, idA=None, idB=None, idC=None, idD = None, minFrame=None, maxFrame=None ):
            
    global eventCacheDico_
    
    if eventCacheEnable_ == True:
    
        print ("Cache debug:", connection, file, eventName, "ids:" , idA, idB, idC, idD, "frames:", minFrame, maxFrame )
        
        
        if (file, eventName, idA, idB, idC, idD, minFrame, maxFrame) in eventCacheDico_: 
            eventTimeLine = eventCacheDico_[ file, eventName, idA, idB, idC, idD, minFrame, maxFrame ]
            print ( eventName , " Id(",idA ,",", idB, ",", idC, "," , idD , ") Loaded from cache (" , len( eventTimeLine.eventList ) , " records. )")
            return eventTimeLine

        
    eventTimeLine = EventTimeLine( connection, eventName , idA = idA, idB = idB, idC = idC, idD = idD, minFrame = minFrame, maxFrame = maxFrame )
    
    if eventCacheEnable_ == True:
        print ( "Caching eventTimeLine")
        eventCacheDico_[ file, eventName, idA, idB, idC, idD, minFrame, maxFrame ] = eventTimeLine
    else:
        print( "Loading event from base (Cache event disabled)")
    
    return eventTimeLine
        
def flushEventTimeLineCache():
    eventCacheDico_.clear()