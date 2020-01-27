'''
Created on 25 sept. 2018

@author: Fab
'''
from lmtanalysis.Event import EventTimeLine

eventCacheDico_={}
eventCacheEnable_ = True

def disableEventTimeLineCache():
    ''' If you are using a computer with small amount of RAM, it might be better to disable cache '''
    eventCacheDico_.clear()
    global eventCacheEnable_
    eventCacheEnable_ = False
    print( "Cache event is disabled" )
    
    
def EventTimeLineCached( connection, file, eventName, idA=None, idB=None, idC=None, idD = None, minFrame=None, maxFrame=None, loadEventWithoutOverlapCheck=False ):
            
    global eventCacheDico_
    
    if eventCacheEnable_ == True:
    
        #print ("Cache debug:", connection, file, eventName, "ids:" , idA, idB, idC, idD, "frames:", minFrame, maxFrame , loadEventWithoutOverlapCheck )
        
        
        if (file, eventName, idA, idB, idC, idD, minFrame, maxFrame, loadEventWithoutOverlapCheck ) in eventCacheDico_: 
            eventTimeLineVoc = eventCacheDico_[ file, eventName, idA, idB, idC, idD, minFrame, maxFrame, loadEventWithoutOverlapCheck ]
            print ( eventName , " Id(",idA ,",", idB, ",", idC, "," , idD , ") Loaded from cache (" , len( eventTimeLineVoc.eventList ) , " records. )")
            return eventTimeLineVoc

        
    eventTimeLineVoc = EventTimeLine( connection, eventName , idA = idA, idB = idB, idC = idC, idD = idD, minFrame = minFrame, maxFrame = maxFrame , loadEventIndependently = loadEventWithoutOverlapCheck )
    
    if eventCacheEnable_ == True:
        print ( "Caching eventTimeLineVoc")
        eventCacheDico_[ file, eventName, idA, idB, idC, idD, minFrame, maxFrame, loadEventWithoutOverlapCheck ] = eventTimeLineVoc
    else:
        print( "Loading event from base (Cache event disabled)")
    
    return eventTimeLineVoc
        
def flushEventTimeLineCache():
    eventCacheDico_.clear()