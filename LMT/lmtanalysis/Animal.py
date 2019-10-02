'''
Created on 7 sept. 2017

@author: Fab
'''

from lmtanalysis.Detection import *

#matplotlib fix for mac
import matplotlib
matplotlib.use('TkAgg' )


import matplotlib.pyplot as plt
from lmtanalysis.Chronometer import *
import matplotlib as mpl
import numpy as np
from mpl_toolkits.mplot3d import *
import matplotlib.ticker
import math
import time
from lmtanalysis.Measure import *
from statistics import *
from scipy.spatial import distance
from scipy.ndimage.measurements import standard_deviation
from statistics import mean
from lmtanalysis.Event import EventTimeLine
from lmtanalysis.Point import Point
from lmtanalysis.Mask import Mask
import matplotlib.patches as mpatches
from lxml import etree
import matplotlib.ticker as ticker
from lmtanalysis.Util import convert_to_d_h_m_s
from lmtanalysis.Util import getDatetimeFromFrame

idAnimalColor = [ None, "red","green","blue","orange"]

def getAnimalColor( animalId ):    
    return idAnimalColor[ animalId ]

class Animal():

    def __init__(self, baseId , RFID , name=None, genotype=None , user1 = None, conn = None ):
        self.baseId = baseId
        self.RFID = RFID
        self.name = name
        self.genotype = genotype
        self.user1 = user1
        self.conn = conn
        self.detectionDictionnary = {}
        

    def __str__(self):        
        return "Animal Id:{id} Name:{name} RFID:{rfid} Genotype:{genotype} User1:{user1}"\
            .format( id=self.baseId, rfid=self.RFID, name=self.name, genotype=self.genotype, user1=self.user1 )

    def getColor(self):
        return getAnimalColor( self.baseId )

    def getDetectionAt(self, t):
        if t in self.detectionDictionnary:
            return self.detectionDictionnary[t]
        return None

    def loadDetection(self, start=None, end=None, lightLoad = False ):
        '''
        lightLoad only loads massX and massY to speed up the load. Then one can only compute basic features such as global speed of the animals
        '''
        print ( self.__str__(), ": Loading detection.")
        chrono = Chronometer("Load detection")

        self.detectionDictionnary.clear()
                
        cursor = self.conn.cursor()
        query =""
        if lightLoad == True :
            query = "SELECT FRAMENUMBER, MASS_X, MASS_Y FROM DETECTION WHERE ANIMALID={}".format( self.baseId )
        else:
            query = "SELECT FRAMENUMBER, MASS_X, MASS_Y, MASS_Z, FRONT_X, FRONT_Y, FRONT_Z, BACK_X, BACK_Y, BACK_Z,REARING,LOOK_UP,LOOK_DOWN FROM DETECTION WHERE ANIMALID={}".format( self.baseId )
            
        if ( start != None ):
            query += " AND FRAMENUMBER>={}".format(start )
        if ( end != None ):
            query += " AND FRAMENUMBER<={}".format(end )
            
        print( query )
        cursor.execute( query )
        
        rows = cursor.fetchall()
        cursor.close()    
        
        for row in rows:
            frameNumber = row[0]
            massX = row[1]
            massY = row[2]
            detection = None
            #filter detection at 0

            if ( massX < 10 ):
                continue

            if not lightLoad:
                massZ = row[3]

                frontX = row[4]
                frontY = row[5]
                frontZ = row[6]
    
                backX = row[7]
                backY = row[8]
                backZ = row[9]
    
                rearing = row[10]
                lookUp = row[11]
                lookDown = row[12]
            
                detection = Detection( massX, massY, massZ, frontX, frontY, frontZ, backX, backY, backZ, rearing, lookUp, lookDown )
            else:
                detection = Detection( massX, massY , lightLoad = True )
            
            self.detectionDictionnary[frameNumber] = detection

        print ( self.__str__(), " ", len( self.detectionDictionnary ) , " detections loaded in {} seconds.".format( chrono.getTimeInS( )) )
    
    
    def getNumberOfDetection(self, tmin, tmax):
        
        
        return len ( self.detectionDictionnary.keys() )
    
    
    def filterDetectionByInstantSpeed(self , minSpeed, maxSpeed ):
        """
        speed function in LMT use t-1 and t+1 detection to provide a result.
        here we remove spurious tracking jump, so we check on t to t+1 frame.
        speed is in cm per second
        """
        nbRemoved = 0
        for key in sorted(self.detectionDictionnary.keys()):
            a = self.detectionDictionnary.get( key )
            b = self.detectionDictionnary.get( key+1 )
                        
            if ( b==None or a==None):
                continue
            
            speed = math.hypot( a.massX - b.massX, a.massY - b.massY )*scaleFactor/(1/30)
        
            if ( speed > maxSpeed or speed < minSpeed ):
                self.detectionDictionnary.pop( key )
                nbRemoved+=1
        
        print( "Filtering Instant speed min:",minSpeed, "max:",maxSpeed, "number of detection removed:", nbRemoved )
    
    def filterDetectionByArea(self, x1, y1, x2, y2 ):
        '''
        filter detection in the cage ( using centimeter, starting at top left of the cage )
        '''
        nbRemoved = 0
        for key in sorted(self.detectionDictionnary.keys()):
            a = self.detectionDictionnary.get( key )

            if ( a==None):
                continue
            
            x = (a.massX - cornerCoordinates50x50Area[0][0] )* scaleFactor
            y = (a.massY - cornerCoordinates50x50Area[0][1] )* scaleFactor            
        
            if ( x < x1 or x > x2 or y < y1 or y > y2 ):
                self.detectionDictionnary.pop( key )
                nbRemoved+=1
        
        print( "Filtering area, number of detection removed:", nbRemoved )
    
    def filterDetectionByEventTimeLine( self, eventTimeLine ):
        '''
        filter detection using an event. Keep only what matches the event
        '''
        eventDic = eventTimeLine.getDictionnary()
        nbRemoved = 0
        for key in sorted( self.detectionDictionnary.keys() ):
            a = self.detectionDictionnary.get( key )

            if ( a==None):
                continue

            if not ( key in eventDic ):
                self.detectionDictionnary.pop( key )        
                nbRemoved+=1
        
        print( "Filtering area, number of detection removed:", nbRemoved )
        
    def clearDetection(self):
        
        self.detectionDictionnary.clear()
    
    def getMaxDetectionT(self):
        """
        returns the timepoint of the last detection.
        """
        
        if len ( self.detectionDictionnary.keys() ) == 0:
            return None
        
        return sorted(self.detectionDictionnary.keys())[-1]
    
    def getTrajectoryData( self , maskingEventTimeLine=None ):
        
        keyList = sorted(self.detectionDictionnary.keys())
        
        if maskingEventTimeLine!=None:
            keyList = maskingEventTimeLine.getDictionnary()
        
        xList = []
        yList = []
        
        previousKey = 0
        

        for key in keyList:
            
            #print ( "key:", key, "value", self.getSpeed( key ) , "previous:" , previousKey )
            
            if previousKey+1 != key:                
                xList.append( [np.nan, np.nan] )
                yList.append( [np.nan, np.nan] )
                previousKey = key

                #print("break previous")
                continue
            previousKey = key
            
            a = self.detectionDictionnary.get( key )
            if ( a==None):
                xList.append( [np.nan, np.nan] )
                yList.append( [np.nan, np.nan] )
                #print("break none A")
                continue
            b = self.detectionDictionnary.get( key+1 )
            if ( b==None):
                xList.append( [np.nan, np.nan] )
                yList.append( [np.nan, np.nan] )
                #print("break none B")
                continue
            
            xList.append( [a.massX,b.massX] )
            yList.append( [-a.massY,-b.massY] )
        
        return xList, yList
    
    
    def plotTrajectory(self , show=True, color='k', maskingEventTimeLine=None, title = "" ):
        
        print ("Draw trajectory of animal " + self.name )
        
        xList, yList = self.getTrajectoryData( maskingEventTimeLine )
            
        plt.plot( xList, yList, color=color, linestyle='-', linewidth=1, alpha=0.5, label= self.name )
        plt.title( title + self.RFID )
        plt.xlim(90, 420)
        plt.ylim(-370, -40)
        
        if ( show ):
            plt.show()    


    def plotTrajectory3D(self):
        
        print ("Draw 3D trajectory")
        keyList = sorted(self.detectionDictionnary.keys())
        
        mpl.rcParams['legend.fontsize'] = 10

        fig = plt.figure()
        ax = fig.gca(projection='3d')
        theta = np.linspace(-4 * np.pi, 4 * np.pi, 100)
        
        z = np.linspace(-2, 2, 100)
        r = z**2 + 1
        x = r * np.sin(theta)
        y = r * np.cos(theta)
        
        '''
        print ( z )
        print ( r )
        print ( x )
        print ( y )
        '''
        
        xList = []
        yList = []
        zList = []
    
        for key in keyList:
            
            a = self.detectionDictionnary.get( key )
            b = self.detectionDictionnary.get( key+1 )
            if ( b==None):
                continue
            
            xList.append( a.massX )
            yList.append( a.massY )
            zList.append( a.massZ )
            
        ax.plot(xList, yList, zList, label= "3D Trajectory of " + self.RFID )
        ax.legend()
        
        plt.show()
    
    
    def getDistancePerBin(self , binFrameSize , minFrame=0, maxFrame=None ):
        if ( maxFrame==None ):
            maxFrame= self.getMaxDetectionT()
        
        distanceList = []
        t = minFrame
        while ( t < maxFrame ):
            distanceBin = self.getDistance( t , t+binFrameSize )
            print( "Distance bin n:{} value:{}".format ( t , distanceBin ) )
            distanceList.append( distanceBin )
            t=t+binFrameSize
        
        return distanceList
     
        
    def getDistance(self , tmin=0, tmax= None ):
        '''
        Returns the distance traveled by the animal (in cm)        
        '''
        
        print("Compute total distance min:{} max:{} ".format( tmin , tmax ))
        keyList = sorted(self.detectionDictionnary.keys())
        
        if ( tmax==None ):
            tmax= self.getMaxDetectionT()
    
        totalDistance = 0
        for key in keyList:
            
            if ( key <= tmin or key >= tmax ):
                continue
            
            a = self.detectionDictionnary.get( key )
            b = self.detectionDictionnary.get( key+1 )
                        
            if ( b==None):
                continue
            
            if (math.hypot( a.massX - b.massX, a.massY - b.massY )>85.5): #if the distance calculated between two frames is too large, discard
                continue
            
            totalDistance += math.hypot( a.massX - b.massX, a.massY - b.massY )
        
        totalDistance *= scaleFactor
            
        return totalDistance
    
    def getOrientationVector(self, t):
        
        d = self.detectionDictionnary.get( t )
        
        if d == None:
            return None

        if d.frontX == None:
            return None
        
        if d.backX == None:
            return None
        
        deltaX = d.frontX - d.backX
        deltaY = d.frontY - d.backY
        p = Point( deltaX, deltaY )
        return p

    def getSpeedVector(self, t):
        
        a = self.detectionDictionnary.get( t-1 )
        b = self.detectionDictionnary.get( t+1 )
        
        if a == None or b == None:
            return None
            
        speedVectorX = a.massX - b.massX
        speedVectorY = a.massY - b.massY

        p = Point( speedVectorX, speedVectorY )
        return p

    def getFrontSpeed(self, t):
        
        a = self.detectionDictionnary.get( t-1 )
        b = self.detectionDictionnary.get( t+1 )
        
        if a == None or b == None:
            return None
            
        speedVectorX = a.frontX - b.frontX
        speedVectorY = a.frontY - b.frontY

        p = Point( speedVectorX, speedVectorY )
        return p
    
    def getBackSpeed(self, t):
        
        a = self.detectionDictionnary.get( t-1 )
        b = self.detectionDictionnary.get( t+1 )
        
        if a == None or b == None:
            return None
            
        speedVectorX = a.backX - b.backX
        speedVectorY = a.backY - b.backY

        p = Point( speedVectorX, speedVectorY )
        return p
    
    
    def getDistanceSpecZone(self, tmin=0, tmax=None, xa=None, ya=None, xb=None, yb=None):

        keyList = sorted(self.detectionDictionnary.keys())
        
        if ( tmax==None ):
            tmax = self.getMaxDetectionT()
    
        distance = 0

        for key in keyList:
            
            if ( key <= tmin or key >= tmax ):
                #print ( 1 )
                continue
            
            a = self.detectionDictionnary.get( key )
            b = self.detectionDictionnary.get( key+1 )
            
            if ( b==None):
                continue
            
            if (a.massX<xa or a.massX>xb or a.massY<ya or a.massY>yb or b.massX<xa or b.massX>xb or b.massY<ya or b.massY>yb):
                #print ( 2 )
                continue
            
            if (math.hypot( a.massX - b.massX, a.massY - b.massY )>85.5): #if the distance calculated between two frames is too large, discard
                continue
            
            distance += math.hypot( a.massX - b.massX, a.massY - b.massY )
            
        distance *= scaleFactor
        
        return distance
    
    
    def getDistanceTo (self, t, animalB):
        '''
        determine the distance between the focal animal and another one specified in argument at one specified time point t
        check before that both animals are detected at this time point
        '''
        distanceTo = None

        if ( not ( t in animalB.detectionDictionnary ) ):
            return None

        if ( not ( t in self.detectionDictionnary ) ):
            return None
        
        if (animalB.detectionDictionnary[t].massX == None):
            return None
        
        if (math.hypot( self.detectionDictionnary[t].massX - animalB.detectionDictionnary[t].massX, self.detectionDictionnary[t].massY - animalB.detectionDictionnary[t].massY ) > 71*57/10): #if the distance calculated between the two individuals is too large, discard
            return None
        
        else:
            distanceTo = math.hypot( self.detectionDictionnary[t].massX - animalB.detectionDictionnary[t].massX, self.detectionDictionnary[t].massY - animalB.detectionDictionnary[t].massY )
            return distanceTo
        
        
    def getDistanceToPoint (self, t, xPoint, yPoint):
        '''
        determine the distance between the focal animal and a specific point in the arena at one specified time point t
        '''
        distanceToPoint = None

        if ( not ( t in self.detectionDictionnary ) ):
            return None
        
        if (math.hypot( self.detectionDictionnary[t].massX - xPoint, self.detectionDictionnary[t].massY - yPoint ) > MAX_DISTANCE_THRESHOLD): #if the distance calculated is too large, discard
            return None
        
        else:
            distanceToPoint = math.hypot( self.detectionDictionnary[t].massX - xPoint, self.detectionDictionnary[t].massY - yPoint )
            return distanceToPoint
            
    
    def getMeanBodyLength (self, tmin=0, tmax=None): 
        '''
        determine the mean body length over the time window specified
        '''
        keyList = sorted(self.detectionDictionnary.keys())
        
        if ( tmax==None ):
            tmax= self.getMaxDetectionT()
    
        if ( tmax==None ):
            self.meanBodyLength = None
            return self.meanBodyLength

        bodySizeList = []

        for key in keyList:
            
            if ( key <= tmin or key >= tmax ):
                continue
            
            a = self.detectionDictionnary.get( key )
            bodySizeList.append(a.getBodySize())
            
        mean = np.nanmean(bodySizeList)
        print( "mean animal bodysize: "  , mean )
        
        self.meanBodyLength = mean
        
        return self.meanBodyLength
    
    
    def getBodyThreshold (self, tmin=0, tmax=None): 
        '''
        determine the body size threshold used to determine SAP
        '''
        keyList = sorted(self.detectionDictionnary.keys())
        
        if ( tmax==None ):
            tmax= self.getMaxDetectionT()
    
        bodySizeList = []

        for key in keyList:
            
            if ( key <= tmin or key >= tmax ):
                continue
            
            a = self.detectionDictionnary.get( key )
            bodySizeList.append(a.getBodySize())
            
        #verifier si ce calcul tourne bien:
        threshold = np.nanmean(bodySizeList) + np.nanstd(bodySizeList)
        
        self.bodyThreshold = threshold
        
        return self.bodyThreshold
    
    
    def getMedianBodyHeight (self, tmin=0, tmax=None): 
        '''
        determine the body size threshold used to determine SAP
        '''
        keyList = sorted(self.detectionDictionnary.keys())
        
        if ( tmax==None ):
            tmax= self.getMaxDetectionT()
    
        bodyHeightList = []

        for key in keyList:
            
            if ( key <= tmin or key >= tmax ):
                continue
            
            a = self.detectionDictionnary.get( key )
            bodyHeightList.append(a.massZ)
            
        self.medianBodyHeight = np.median(np.array(bodyHeightList))
        
        return self.medianBodyHeight
    
    
    def getThresholdMassHeight (self, tmin=0, tmax=None): 
        '''
        determine the body size height threshold used to determine whether the animal is rearing or not
        here we use the 7th decile
        '''
        keyList = sorted(self.detectionDictionnary.keys())
        
        if ( tmax==None ):
            tmax= self.getMaxDetectionT()
    
        massHeightList = []

        for key in keyList:
            
            if ( key <= tmin or key >= tmax ):
                continue
            
            a = self.detectionDictionnary.get( key )
            massHeightList.append(a.massZ)
        
        decile = 7*len(massHeightList)/10
        print("7eme decile mass:")
        print(decile)
        print("arrondi massZ:")
        print(math.ceil(decile)-1)
            
        self.eightDecileMassHeight = sorted(massHeightList)[math.ceil(decile)-1]
        
        return self.eightDecileMassHeight
    
    
    def getThresholdFrontHeight (self, tmin=0, tmax=None): 
        '''
        determine the body size height threshold used to determine whether the animal is rearing or not
        here we use the 7th decile
        '''
        keyList = sorted(self.detectionDictionnary.keys())
        
        if ( tmax==None ):
            tmax= self.getMaxDetectionT()
    
        frontHeightList = []

        for key in keyList:
            
            if ( key <= tmin or key >= tmax ):
                continue
            
            a = self.detectionDictionnary.get( key )
            frontHeightList.append(a.frontZ)
        
        decile = 7*len(frontHeightList)/10
        print("7eme decile front:")
        print(decile)
        print("arrondi frontZ:")
        print(math.ceil(decile)-1)
            
        self.eightDecileFrontHeight = sorted(frontHeightList)[math.ceil(decile)-1]
        
        return self.eightDecileFrontHeight
    
    
    def getDirection(self, t):
        '''
        determines the direction of the animal using the head and the mass center
        '''
        a = self.detectionDictionnary.get( t )
        return a.getDirection();
            
    
    def getSpeed(self , t ):
        '''
        calculate the instantaneous speed of the animal at each frame
        '''
        a = self.detectionDictionnary.get( t-1 )
        b = self.detectionDictionnary.get( t+1 )
                        
        if ( b==None or a==None):
            return None
            
        speed = math.hypot( a.massX - b.massX, a.massY - b.massY )*scaleFactor/(2/30)
        
        return speed
    
    
    def getVerticalSpeed(self , t ):
        '''
        calculate the instantaneous vertical speed of the mass center of the animal at each frame
        '''
        a = self.detectionDictionnary.get( t-1 )
        b = self.detectionDictionnary.get( t+1 )
                        
        if ( b==None or a==None):
            return None
            
        verticalSpeed = (b.massZ - a.massZ)/2
        
        return verticalSpeed
    
    
    def getSap(self, tmin=0, tmax=None, xa=None, ya=None, xb=None, yb=None):
        print("Compute number of frames in SAP in specific zone of the cage")
    
        self.getBodyThreshold( )
        self.getMedianBodyHeight()
    
        #TODO: pas mettre body threshold en self car ... c'est pas la peine.
    
        keyList = sorted(self.detectionDictionnary.keys())
    
        if ( tmax==None ):
            tmax = self.getMaxDetectionT()
    
        sapList = []
        
        for key in keyList:
            
            if ( key <= tmin or key >= tmax ):
                #print ( 1 )
                continue
            
            detection = self.detectionDictionnary.get(key);
            if (detection.massX<xa or detection.massX>xb or detection.massY<ya or detection.massY>yb or detection.massZ>self.medianBodyHeight):
                #print ( 2 )
                continue
    
            speed = self.getSpeed( key )
            if ( speed == None ):
                #print ( 3 )
                continue
    
            if (detection.getBodySize( ) >=self.bodyThreshold and speed<SPEED_THRESHOLD_LOW and detection.massZ<self.medianBodyHeight):
                #print ( 4 )
                sapList.append( detection )

        return sapList
          
      
    def getSapDictionnary(self, tmin=0, tmax=None ):
        
        self.getBodyThreshold( )
        self.getMedianBodyHeight()
        
        keyList = sorted(self.detectionDictionnary.keys())
        
        if ( tmax==None ):
            tmax = self.getMaxDetectionT()
    
        sapDictionnary = {}
        
        for key in keyList:
            
            if ( key <= tmin or key >= tmax ):
                continue
            
            detection = self.detectionDictionnary.get(key);

            speed = self.getSpeed( key )
            if ( speed == None ):
                continue

            if (detection.getBodySize( ) >=self.bodyThreshold and speed<SPEED_THRESHOLD_LOW and detection.massZ<self.medianBodyHeight):
                sapDictionnary[key] = True

        return sapDictionnary
        
    
    def getCountFramesSpecZone(self, tmin=0, tmax=None, xa=None, ya=None, xb=None, yb=None):
        '''
        coordinates are in pixel
        '''
        keyList = sorted(self.detectionDictionnary.keys())
        
        if ( tmax==None ):
            tmax = self.getMaxDetectionT()
    
        count =0

        for key in keyList:
            
            if ( key <= tmin or key >= tmax ):
                #print ( 1 )
                continue
            
            detection = self.detectionDictionnary.get(key);
            if (detection.massX<xa or detection.massX>xb or detection.massY<ya or detection.massY>yb):
                #print ( 2 )
                continue

            count+=1
            
        return count
        
    
    def plotDistance(self, color='k' , show=True ):
        print ("Plot distance")
        keyList = sorted(self.detectionDictionnary.keys())
        
        tList = []
        distanceList = []
    
        totalDistance = 0
        for key in keyList:
            
            a = self.detectionDictionnary.get( key )
            b = self.detectionDictionnary.get( key+1 )
                        
            if ( b==None):
                continue
            
            totalDistance += math.hypot( a.massX - b.massX, a.massY - b.massY )
            
            tList.append( key / 30 / 60 )
            distanceList.append( totalDistance )
        
        #fig,ax = plt.subplots()
        plt.plot( tList, distanceList, color=color, linestyle='-', linewidth=2 , label="Cumulated distance of " + self.__str__() )
        
        #formatter = matplotlib.ticker.FuncFormatter(lambda frame, x: time.strftime('%Hh%Mm%Ss', time.gmtime( frame // 30)))
        #formatter = matplotlib.ticker.FuncFormatter(lambda frame, x: time.strftime('%Hh%Mm', time.gmtime( frame // 30)))
        #ax.xaxis.set_major_formatter( formatter )                        
        #ax.xaxis.set_minor_locator( matplotlib.ticker.MultipleLocator(30*60) )
        #ax.xaxis.set_major_locator( matplotlib.ticker.MultipleLocator(30*60*10) )
        
        plt.legend()
        
        if ( show ):
            plt.show()        
    
    
    def getBinaryDetectionMask(self , t):
        '''
        returns the mask of a detection at a given T.
        '''
        query = "SELECT DATA FROM DETECTION WHERE ANIMALID={} AND FRAMENUMBER={}".format( self.baseId , t )

        #print( "TEST")
        #print( query )
        cursor = self.conn.cursor()
        cursor.execute( query )
        
        rows = cursor.fetchall()
        cursor.close()    
        
        
        
        if ( len(rows)!=1 ):
            print ("unexpected number of row: " , str( len(rows ) ) )
            return None
        
        row = rows[0]        
        data = row[0]
        
        #print( data )        
        
        x = 0
        y = 0
        w = 0
        h = 0
        boolMaskData = None
        
        tree = etree.fromstring( data )
        for user in tree.xpath("/root/ROI/boundsX"):
            x = int(user.text)
        for user in tree.xpath("/root/ROI/boundsY"):
            y = int(user.text)
        for user in tree.xpath("/root/ROI/boundsW"):
            w = int(user.text)
        for user in tree.xpath("/root/ROI/boundsH"):
            h = int(user.text)
        for user in tree.xpath("/root/ROI/boolMaskData"):
            boolMaskData = user.text

        mask = Mask( x , y , w , h , boolMaskData, self.getColor() )

        '''
        <boundsX>119</boundsX><boundsY>248</boundsY><boundsW>37</boundsW><boundsH>29</boundsH>
        <boolMaskData>78:5e:bd:d3:4b:e:c0:20:8:4:d0:e9:fd:2f:dd:a0:56:11:87:cf:a2:91:a5:be:c:24:22:c0:ea:91:62:17:eb:ac:91:84:4d:13:84:29:e3:aa:cd:70:65:8:1b:8c:90:83:39:66:eb:59:30:2e:51:41:17:cc:7c:c2:a0:d7:9a:a8:82:42:33:da:e5:26:16:63:a2:3f:50:5f:d7:24:a9:82:be:bd:77:a3:a0:be:b:45:f6:37:11:64:9:60:d0:9:e4:44:23:2e:b4:f2:45:bf:91:b4:c8:bc:14:f1:2:7a</boolMaskData></ROI></
        '''
        
        return mask

        '''
        mask = Mask( x , y , binaryMask )
        
        return mask
        '''


    
class AnimalPool():
    """
    Manages a pool of animals.
    """
    
    def __init__(self):

        self.animalDictionnary = {}
        
    def getAnimalDictionnary(self):
        return self.animalDictionnary
    
    def getAnimalWithId(self , id):
        return self.animalDictionnary[id]
    
    def getAnimalList(self):
        
        animalList= []
        
        for k in self.animalDictionnary:
            animal = self.animalDictionnary[k] 
            animalList.append( animal )
        
        return animalList
        
    def loadAnimals( self, conn ):
        
        print ("Loading animals.")
        
        cursor = conn.cursor()
        self.conn = conn        
    
        # Check the number of row available in base
        query = "SELECT * FROM ANIMAL"
        cursor.execute( query )
        field_names = [i[0] for i in cursor.description]
        print ( "Fields available in lmtanalysis: " , field_names )
        
        #build query
        query = "SELECT "
        nbField = len( field_names )
        if ( nbField == 3 ):
            query+="ID,RFID,NAME"
        elif ( nbField == 4 ):
            query+="ID,RFID,NAME,GENOTYPE"
        elif ( nbField == 5 ):
            query+="ID,RFID,NAME,GENOTYPE,IND"
        
        query += " FROM ANIMAL ORDER BY GENOTYPE"
        print ( "SQL Query: " + query )
        
        cursor.execute( query )
        rows = cursor.fetchall()
        cursor.close()    
        
        self.animalDictionnary.clear()
                
        for row in rows:
            
            animal = None
            if ( len( row ) == 3 ):
                animal = Animal( row[0] , row[1] , name=row[2] , conn = conn )
            if ( len( row ) == 4 ):
                animal = Animal( row[0] , row[1] , name=row[2] , genotype=row[3] , conn = conn )
            if ( len( row ) == 5 ):
                animal = Animal( row[0] , row[1] , name=row[2] , genotype=row[3] , user1=row[4] , conn = conn )
            
            if ( animal!= None):
                self.animalDictionnary[animal.baseId] = animal
                print ( animal )
            else:
                print ( "Animal loader : error while loading animal.")
        
    def loadDetection (self , start = None, end=None , lightLoad = False ):
        for animal in self.animalDictionnary.keys():
            self.animalDictionnary[animal].loadDetection( start = start, end = end , lightLoad=lightLoad )

    def filterDetectionByInstantSpeed(self, minSpeed, maxSpeed):
        for animal in self.animalDictionnary.keys():
            self.animalDictionnary[animal].filterDetectionByInstantSpeed( minSpeed, maxSpeed )

    def filterDetectionByArea(self, x1, y1, x2, y2 ):
        for animal in self.animalDictionnary.keys():
            self.animalDictionnary[animal].filterDetectionByArea( x1, y1, x2, y2 )

    def filterDetectionByEventTimeLine(self, eventTimeLine ):
        for animal in self.animalDictionnary.keys():
            self.animalDictionnary[animal].filterDetectionByEventTimeLine( eventTimeLine )

    def getGenotypeList(self):
        
        genotype = {}
        
        for k in self.animalDictionnary:
            animal = self.animalDictionnary[k] 
            genotype[animal.genotype] = True
                
        return genotype.keys()
    
    def getAnimalsWithGenotype(self, genotype ):
        
        resultList= []
        
        for k in self.animalDictionnary:
            animal = self.animalDictionnary[k] 
            if ( animal.genotype == genotype ):
                resultList.append( animal )
                
        return resultList
        
        #return [x for x in self.animalDictionnary if x.genotype==genotype ]

    def getNbAnimals(self):
        return len(self.animalDictionnary)
    
    def getMaxDetectionT(self):
        """
        returns the timepoint of the last detection of all animals
        """
        maxFrame = 0
        for animal in self.getAnimalList():
            maxFrame = max( maxFrame, animal.getMaxDetectionT() )
        
        return maxFrame
    
    def frameToTimeTicker(self, x, pos):
        vals= convert_to_d_h_m_s( x )
        experimentTime = "D{0} - {1:02d}:{2:02d}".format( int(vals[0])+1, int(vals[1]), int(vals[2]) )
       
        realTime = ""
        if x > 0:
            datetime = getDatetimeFromFrame( self.conn , x )
            if datetime != None:
                realTime = "\n" + getDatetimeFromFrame( self.conn , x ).strftime('%d-%m (%b)-%Y %H:%M:%S')
        
        return experimentTime + realTime

    def plotSensorData( self , sensor="TEMPERATURE", show = True , saveFile = None , minValue=0 ):
        """
        plots data for temperature
        """
        print( "plotting sensor data. " , sensor )
        cursor = self.conn.cursor()
    
        # Check the number of row available in base
        query = "SELECT FRAMENUMBER,"+sensor+" FROM FRAME"
        try:
            cursor.execute( query )
        except:
            print("plot sensor data: can't access data for ", sensor )
            return
            
        rows = cursor.fetchall()
        cursor.close()    
        
        frameNumberList = []
        sensorValueList = []        
        for row in rows:
            
            sensorValue = row[1]
            if ( sensorValue > minValue ):
                frameNumberList.append( row[0] )
                sensorValueList.append( sensorValue )

        fig, ax = plt.subplots( nrows = 1 , ncols = 1 , figsize=( 12, 4 ) )
        
        ''' set x axis '''
        formatter = ticker.FuncFormatter( self.frameToTimeTicker )
        ax.xaxis.set_major_formatter(formatter)
        ax.tick_params(labelsize=6 )
        ax.xaxis.set_major_locator(ticker.MultipleLocator( 30 * 60 * 60 * 12 ))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator( 30 * 60 * 60 ))
        
        ax.plot( frameNumberList, sensorValueList, color= "black" , linestyle='-', linewidth=1, label= sensor )
        ax.legend( loc=1 )
        
        # plot night
        nightTimeLine = EventTimeLine( self.conn, "night" , None, None, None , None )        
        for nightEvent in nightTimeLine.eventList:
            
            ax.axvspan( nightEvent.startFrame, nightEvent.endFrame, alpha=0.1, color='black')
            ax.text( (nightEvent.startFrame+ nightEvent.endFrame)/2 , 0.5 , "dark phase" ,fontsize=8,ha='center')

        if saveFile !=None:
            print("Saving figure : " + saveFile )
            fig.savefig( saveFile, dpi=100)
            
        if ( show ):
            plt.show()
        plt.close()
    
    def createAutomaticDayNightEvent( self ):
        """
        Automatically creates night event with light sensor.
        """
        
        # threshold for light is 115
        lightThreshold= 115
        
        cursor = self.conn.cursor()
    
        # Check the number of row available in base
        query = "SELECT FRAMENUMBER,LIGHTVISIBLE FROM FRAME"
        try:
            cursor.execute( query )
        except:
            print("Can't access lightVisible data")
            return
        
        rows = cursor.fetchall()
        cursor.close()    
        
        frameNumberList = []
        sensorValueList = []        
        allValuesAreZero = True
        
        nightTimeLine = EventTimeLine( None, "night", loadEvent=False )
        dayTimeLine = EventTimeLine( None, "day", loadEvent=False )
        
        resultNight = {}
        resultDay = {}
        
        for row in rows:
            
            sensorValue = row[1]
            frameNumberList.append( row[0] )
            sensorValueList.append( sensorValue )
            if sensorValue != 0:
                allValuesAreZero = False
                
            isNight = sensorValue < lightThreshold
            if isNight:
                resultNight[ row[0] ] = True
            else:
                resultDay[ row[0] ] = True
            
        if allValuesAreZero:
            print("AutoDay/Night: Failed. No sensor record (all values are 0).")
            return
        
        nightTimeLine.reBuildWithDictionnary( resultNight )
        dayTimeLine.reBuildWithDictionnary( resultDay )
                
        nightTimeLine.endRebuildEventTimeLine( self.conn , deleteExistingEvent=True )
        dayTimeLine.endRebuildEventTimeLine( self.conn, deleteExistingEvent=True )
        
    def plotNight(self, show = True , saveFile = None ):
        
        fig, ax = plt.subplots( nrows = 1 , ncols = 1 , figsize=( 12, 4 ) )

        nightTimeLine = EventTimeLine( self.conn, "night" , None, None, None , None )        
        for nightEvent in nightTimeLine.eventList:
            
            ax.axvspan( nightEvent.startFrame, nightEvent.endFrame, alpha=0.1, color='black')
            ax.text( (nightEvent.startFrame+ nightEvent.endFrame)/2 , 0.5 , "dark phase" ,fontsize=8,ha='center')
        
        ''' set x axis '''
        formatter = ticker.FuncFormatter( self.frameToTimeTicker )
        ax.xaxis.set_major_formatter(formatter)
        ax.tick_params(labelsize=6 )
        ax.xaxis.set_major_locator(ticker.MultipleLocator( 30 * 60 * 60 * 12 ))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator( 30 * 60 * 60 ))

        if saveFile !=None:
            print("Saving figure : " + saveFile )
            fig.savefig( saveFile, dpi=100)
            
        if ( show ):
            plt.show()
        plt.close()
        
    def buildSensorData(self, file ):
        print("Build sensor data")
        self.createAutomaticDayNightEvent( )        
        self.plotNight( False , saveFile = file+"_auto day night.pdf" )
        self.plotSensorData( sensor = "TEMPERATURE" , minValue = 10, saveFile = file+"_log_temperature.pdf", show = False )
        self.plotSensorData( sensor = "SOUND" , saveFile = file+"_log_sound level.pdf" , show = False )
        self.plotSensorData( sensor = "HUMIDITY" , minValue = 5 , saveFile = file+"_log_humidity.pdf" ,show = False )        
        self.plotSensorData( sensor = "LIGHTVISIBLE" , minValue = 40 , saveFile = file+"_log_light visible.pdf", show = False  )
        self.plotSensorData( sensor = "LIGHTVISIBLEANDIR" , minValue = 50 , saveFile = file+"_log_light visible and infra.pdf", show = False  )

 
    def plotTrajectory( self , show=True, maskingEventTimeLine=None , title = None, scatter = False, saveFile = None ):
        
        print( "AnimalPool: plot trajectory.")
        nbCols = len( self.getAnimalList() )+1
        fig, axes = plt.subplots( nrows = 1 , ncols = nbCols , figsize=( nbCols*4, 1*4 ) , sharex='all', sharey='all'  )
        
        if title==None:
            title="Trajectory of animals"
        
        #draw all animals
        axis = axes[0]
        legendList=[]
        for animal in self.getAnimalList():
            
            print ("Compute trajectory of animal " + animal.name )
            xList, yList = animal.getTrajectoryData( maskingEventTimeLine )                        
            print ("Draw trajectory of animal " + animal.name )
            if scatter == True:
                axis.scatter( xList, yList, color= animal.getColor() , s=1 , linewidth=1, alpha=0.05, label= animal.RFID )
                legendList.append( mpatches.Patch(color=animal.getColor(), label=animal.RFID) )
            else:
                axis.plot( xList, yList, color= animal.getColor() , linestyle='-', linewidth=1, alpha=0.5, label= animal.RFID )
                
        axis.legend( handles = legendList , loc=1 )
        axis.set_xlim(90, 420)
        axis.set_ylim(-370, -40)
        
        #draw separated animals
        for animal in self.getAnimalList():
            axis = axes[self.getAnimalList().index(animal)+1]
            
            legendList=[]
            
            print ("Compute trajectory of animal " + animal.name )
            xList, yList = animal.getTrajectoryData( maskingEventTimeLine )                        
            print ("Draw trajectory of animal " + animal.name )
            if scatter == True:
                axis.scatter( xList, yList, color= animal.getColor() , s=1 , linewidth=1, alpha=0.05, label= animal.RFID )
                legendList.append( mpatches.Patch(color=animal.getColor(), label=animal.RFID) )
            else:
                axis.plot( xList, yList, color= animal.getColor() , linestyle='-', linewidth=1, alpha=0.5, label= animal.RFID )
                
            axis.legend( handles = legendList , loc=1 )
        
        fig.suptitle( title )
        
        if saveFile !=None:
            print("Saving figure : " + saveFile )
            fig.savefig( saveFile, dpi=100)
            
        if ( show ):
            plt.show()
        plt.close()
    
    def showMask(self, t ):
        '''
        show the mask of all animals in a figure
        '''
        
        fig, ax = plt.subplots()
        ax.set_xlim(90, 420)
        ax.set_ylim(-370, -40)

        for animal in self.getAnimalList():                    
            mask = animal.getBinaryDetectionMask( t )
            mask.showMask( ax=ax )
        
        plt.show()
        
    def getParticleDictionnary(self , start, end ):
        '''
        return the number of particle per frame
        '''  
        
        query = "SELECT * FROM FRAME WHERE FRAMENUMBER>={} AND FRAMENUMBER<={}".format( start, end )
        
        print ( "SQL Query: " + query )

        cursor = self.conn.cursor()        
        cursor.execute( query )
        rows = cursor.fetchall()
        cursor.close()
        
        particleDictionnary = {}    
                        
        for row in rows:
            
            particleDictionnary[ row[0] ] = row[2]
            
        return particleDictionnary
        



