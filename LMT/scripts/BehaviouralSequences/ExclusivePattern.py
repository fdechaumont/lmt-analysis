'''
Created on 22 f�vr. 2022

@author: Elodie
'''

class ExclusivePattern(object):
    
    def __init__(self , eventTimeLineList , tMax = None):

        # find maximum frame over all timelines
        endFrame = 0
        for timeLine in eventTimeLineList:
            self.initMetaDataTimeLine(timeLine) # init metadata ( add the name of events )
            endFrame = max( endFrame, timeLine.getMaxT() )
        
        if tMax != None: # set endFrame with tMax of user.
            endFrame = tMax
        
        print( "EndFrame = " , endFrame )
        
        self.eventList = [] # init list of ordered exclusive events.
        
        lastEvent = None # last we put in list
        
        for t in range ( 0 , endFrame+1 ): # loop over all frames
            
            found = False # flag set if an event is found. Also used to check if 2 events are found        
            
            for timeLine in eventTimeLineList:
                event = timeLine.getEventAt( t ) # get event at t - todo improve speed
                if event != None:
                    if found == True:
                        print( "Error: timelines are not exclusive : at t= " , t )
                        quit()                    
                    found = True
                    print( t , event )
                    if lastEvent != event:
                        self.eventList.append( event )
                        lastEvent = event #update last event found
            if found == False:
                print("Error: trou in the timelines unexpected ! at t = " , t )
                quit()
                
        self.printEvents()
            
        print("Exclusive Pattern: init done.")
        
    def findPattern(self, pattern ): 
        print( "Init find pattern")
        #pattern = ["e1","e2"]
        
        resultList = []
        
        for index in range( len( self.eventList ) - len( pattern ) +1 ):
            #print( index )
            matchOk = True
            for seekIndex in range ( len( pattern ) ):            
                if pattern[seekIndex ] == "x": # joker
                    continue
                if self.eventList[index+seekIndex ].metadata["name"] != pattern[seekIndex ]:
                    matchOk = False
            if matchOk:
                print( "Pattern found (starting) at t " , index )
                resultList.append( index )
        
        return resultList 

    def printEvents(self):
        for event in self.eventList:
            print( event, event.metadata )

    def initMetaDataTimeLine( self, timeLine ):
    
        for event in timeLine.eventList:
            if event.metadata == None:
                event.metadata = {}
            event.metadata["name"] = timeLine.eventName        
            
    def removeEventsShorterThan(self , duration ):
        
        i = 0
        for event in list( self.eventList ):            
            if event.duration() < duration:            
                self.eventList.remove( event )
                i+=1
        print("Number of event removed: " , i )
        
        