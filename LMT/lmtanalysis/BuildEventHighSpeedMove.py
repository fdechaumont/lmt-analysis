'''
Created on 24 juin 2022

@author: eye
'''
from lmtanalysis.Event import deleteEventTimeLineInBase, EventTimeLine
from lmtanalysis.Animal import AnimalPool
from lmtanalysis.EventTimeLineCache import EventTimeLineCached

def flush( connection ):
    ''' flush event in database '''
    deleteEventTimeLineInBase(connection, "Move high speed" )
    
def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None ): 
    
    ''' use the pool provided or create it'''
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )
        pool.loadDetection( start = tmin, end = tmax )

    '''
    Event Move high speed:
    - the animals is moving at a speed > HIGH_SPEED_MOVE_THRESHOLD
    - the events are merged if they are too close from one another (less than one frame apart) 
    
    '''
    
    eventName = "Move high speed"
    moveIsolatedTimeLine = {}
    moveInContactTimeLine = {}
    highSpeedMoveTimeLine = {}
    
    for animal in pool.animalDictionnary.keys():
        #create the timeline for the high speed move
        highSpeedMoveTimeLine[animal] = EventTimeLine( None, eventName , animal , None , None , None , loadEvent=False )
        # load timelines for move isolated and move in contact
        moveIsolatedTimeLine[animal] = EventTimeLineCached( connection, file, 'Move isolated', animal, minFrame=tmin, maxFrame=tmax )
        moveInContactTimeLine[animal] = EventTimeLineCached( connection, file, 'Move in contact', animal, minFrame=tmin, maxFrame=tmax )
    
    moveTimeLineList = [moveIsolatedTimeLine, moveInContactTimeLine]
    
    resHighSpeedMove = {}
    
    for animal in pool.animalDictionnary.keys():
        resHighSpeedMove[animal] = {} #initialize the dictionary of frames in which the animal is at a high speed
        for moveTimeLine in moveTimeLineList: # loop for both move isolated and move in contact
            for event in moveTimeLine[animal].getEventList(): #loop over each move event
                eventStart = event.startFrame
                eventEnd = event.endFrame
                for t in range( eventStart, eventEnd+1):
                    instantSpeed = pool.animalDictionnary[animal].getSpeed(t)
                    if instantSpeed == None:
                        continue
                    if instantSpeed >= pool.animalDictionnary[animal].parameters.HIGH_SPEED_MOVE_THRESHOLD:
                        resHighSpeedMove[animal][t] = True # select the frame if the animal is moving fast
                        
        highSpeedMoveTimeLine[animal].reBuildWithDictionnary( resHighSpeedMove[animal] )
        highSpeedMoveTimeLine[animal].mergeCloseEvents(1)
        highSpeedMoveTimeLine[animal].removeEventsBelowLength(maxLen=3)
        highSpeedMoveTimeLine[animal].endRebuildEventTimeLine(connection)
                        
    
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build Event Move high speed" , tmin=tmin, tmax=tmax )

    print( "Rebuild event Move high speed finished." )
