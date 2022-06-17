'''
Created on 13 sept. 2017

@author: Fab
'''
from lmtanalysis.Point import Point

class ParametersRat():

    ''' scale to convert distances from pixels to cm '''
    scaleFactor = 20/57
    
    ''' '''
    SPEED_THRESHOLD_LOW = 5
    SPEED_THRESHOLD_HIGH = 10
    
    ''' slope of the body between the nose and the tail basis '''
    BODY_SLOPE_THRESHOLD = 40
    
    ''' threshold for the distance contact using mass center between two detection '''
    DISTANCE_CONTACT_MASS_CENTER = 8/scaleFactor
    
    ''' threshold for the maximum distance allowed between two points '''
    MAX_DISTANCE_THRESHOLD = 71/scaleFactor
    
    ''' threshold min time after a first rearing to detect the second rearing (frames)'''
    SEQUENTIAL_REARING_MIN_TIME_THRESHOLD = 10
    
    ''' threshold max time after a first rearing to detect the second rearing (frames)'''
    SEQUENTIAL_REARING_MAX_TIME_THRESHOLD = 30
    
    ''' threshold for the area around a reared animal for sequential rearing '''
    SEQUENTIAL_REARING_POSITION_THRESHOLD = 50
    
    ''' threshold for the presence within the water zone '''
    MAX_DISTANCE_TO_POINT = 5/scaleFactor
    
    ''' threshold to classify the detection as a rearing; height of the front point'''
    FRONT_REARING_THRESHOLD = 50
    
    ''' threshold to compute head-genital events '''
    MAX_DISTANCE_HEAD_HEAD_GENITAL_THRESHOLD = 15
        
    ''' Cage center in 100x100cm area'''
    cageCenterCoordinatesOpenFieldArea = Point( 256, 208 )
    
    ''' Size of arena in cm '''
    ARENA_SIZE = 100
    
    ''' Margin to define center region in cm (chosen to have same area as non-center)'''
    CENTER_MARGIN = 7.32
    
    ''' Corner Coordinates in 100x100cm area '''
    cornerCoordinatesOpenFieldArea = [
                            (114,63),
                            (398,63),
                            (398,353),
                            (114,353)
                            ]

