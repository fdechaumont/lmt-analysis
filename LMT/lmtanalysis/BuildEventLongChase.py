'''
Created on 13 nov. 2024

@author: eye
'''
from lmtanalysis.Event import deleteEventTimeLineInBase, EventTimeLine
from lmtanalysis.Parameters import getAnimalTypeParameters
from lmtanalysis.Animal import AnimalPool


def flush( connection ):
    ''' flush event in database '''
    print("Flushing longChase" )
    deleteEventTimeLineInBase(connection, "longChase" )
    
def prolongateTimeLine(timeLine, timeLineDic):
    for event in timeLine.eventList:

        t = 0
        # prolongates with timeLineDic
        for t in range(event.startFrame, event.startFrame - 300, -1):
            if not t in timeLineDic:
                break
        event.startFrame = t

        for t in range(event.endFrame, event.endFrame + 300):

            if not t in timeLineDic:
                break
        event.endFrame = t    
        

def reBuildEvent( connection, file, tmin=None, tmax=None, pool = None, animalType = None ): 
    
    """
    LongChase is a succession of events from: Train2, Contact, Follow, Break contact, Escape
    """
    
    #parameters = getAnimalTypeParameters( animalType )
    
    # create dedicated pool as we will alter detection pool with filters (I.e: we don't use the pool cache)
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    
    eventTimeLineTrain2 = {}
    eventTimeLineContact = {}
    eventTimeLineFollow = {}
    eventTimeLineBreak = {}
    eventTimeLineEscapeContact = {}

    for animalA in pool.animalDictionary.keys():
        for animalB in pool.animalDictionary.keys():
            if animalB == animalA:
                print('idA is idB')
                continue
            else:
                eventTimeLineTrain2[(animalA, animalB)] = EventTimeLine(connection, "Train2", idA=animalA, idB=animalB, minFrame=tmin, maxFrame=tmax)
                eventTimeLineContact[(animalA, animalB)] = EventTimeLine(connection, "Contact", idA=animalA, idB=animalB, minFrame=tmin, maxFrame=tmax)
                eventTimeLineFollow[(animalA, animalB)] = EventTimeLine(connection, "FollowZone", idA=animalA, idB=animalB,  minFrame=tmin, maxFrame=tmax)
                eventTimeLineBreak[(animalA, animalB)] = EventTimeLine(connection, "Break contact", idA=animalA, idB=animalB, minFrame=tmin, maxFrame=tmax)
                eventTimeLineEscapeContact[(animalA, animalB)] = EventTimeLine(connection, "Escape contact", idA=animalA,idB=animalB, minFrame=tmin, maxFrame=tmax)
                eventTimeLineFollow[(animalB, animalA)] = EventTimeLine(connection, "FollowZone", idA=animalB, idB=animalA, minFrame=tmin,maxFrame=tmax)
                eventTimeLineBreak[(animalB, animalA)] = EventTimeLine(connection, "Break contact", idA=animalB,idB=animalA, minFrame=tmin, maxFrame=tmax)
                eventTimeLineEscapeContact[(animalB, animalA)] = EventTimeLine(connection, "Escape contact", idA=animalB,idB=animalA, minFrame=tmin, maxFrame=tmax)
                
                eventTimeLineContact[(animalA, animalB)].dilateEvents(10)
                eventTimeLineFollow[(animalA, animalB)].dilateEvents(5)
                eventTimeLineBreak[(animalA, animalB)].dilateEvents(5)
                eventTimeLineEscapeContact[(animalA, animalB)].dilateEvents(5)
                eventTimeLineFollow[(animalB, animalA)].dilateEvents(5)
                eventTimeLineBreak[(animalB, animalA)].dilateEvents(5)
                eventTimeLineEscapeContact[(animalB, animalA)].dilateEvents(5)

                # clean and merge train2 event
                eventTimeLineTrain2[(animalA, animalB)].removeEventsBelowLength(3)
                eventTimeLineTrain2[(animalA, animalB)].mergeCloseEvents(30 * 5)

                #eventTimeLineTrain2Dic = eventTimeLineTrain2[(animalA, animalB)].getDictionary()
                eventTimeLineContactDic = eventTimeLineContact[(animalA, animalB)].getDictionary()
                eventTimeLineFollowABDic = eventTimeLineFollow[(animalA, animalB)].getDictionary()
                eventTimeLineBreakABDic = eventTimeLineBreak[(animalA, animalB)].getDictionary()
                eventTimeLineEscapeContactABDic = eventTimeLineEscapeContact[(animalA, animalB)].getDictionary()
                eventTimeLineFollowBADic = eventTimeLineFollow[(animalB, animalA)].getDictionary()
                eventTimeLineBreakBADic = eventTimeLineBreak[(animalB, animalA)].getDictionary()
                eventTimeLineEscapeContactBADic = eventTimeLineEscapeContact[(animalB, animalA)].getDictionary()

                prolongateTimeLine(eventTimeLineTrain2[(animalA, animalB)], eventTimeLineContactDic)
                prolongateTimeLine(eventTimeLineTrain2[(animalA, animalB)], eventTimeLineFollowABDic)
                prolongateTimeLine(eventTimeLineTrain2[(animalA, animalB)], eventTimeLineBreakABDic)
                prolongateTimeLine(eventTimeLineTrain2[(animalA, animalB)], eventTimeLineEscapeContactABDic)
                prolongateTimeLine(eventTimeLineTrain2[(animalA, animalB)], eventTimeLineFollowBADic)
                prolongateTimeLine(eventTimeLineTrain2[(animalA, animalB)], eventTimeLineBreakBADic)
                prolongateTimeLine(eventTimeLineTrain2[(animalA, animalB)], eventTimeLineEscapeContactBADic)


    print("Creating events")

    longChaseEventTimeLineDic = {}
    for animalA in pool.animalDictionary.keys():
        for animalB in pool.animalDictionary.keys():
            if animalB == animalA:
                print('idA is idB')
                continue
            else:
                longChaseEventTimeLineDic[(animalA, animalB)] = EventTimeLine(None, "longChase", idA=animalA, idB=animalB, loadEvent=False)
                eventTimeLineTrain2[(animalA, animalB)].removeEventsBelowLength(5 * 30)

                for event in eventTimeLineTrain2[(animalA, animalB)].getEventList():
                    longChaseEventTimeLineDic[(animalA, animalB)].addEvent(event)

                longChaseEventTimeLineDic[(animalA, animalB)].endRebuildEventTimeLine(connection)

    # log process
    from lmtanalysis.TaskLogger import TaskLogger

    t = TaskLogger(connection)
    t.addLog("Build Event longChase", tmin=tmin, tmax=tmax)

    print( "Rebuild event finished." )
    return