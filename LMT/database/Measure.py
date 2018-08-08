'''
Created on 13 sept. 2017

@author: Fab
'''

''' scale to convert distances from pixels to cm '''
scaleFactor = 10/57

''' '''
SPEED_THRESHOLD_LOW = 5
SPEED_THRESHOLD_HIGH = 10

''' slope of the body between the nose and the tail basis '''
BODY_SLOPE_THRESHOLD = 40

''' threshold for the maximum distance allowed between two points '''
MAX_DISTANCE_THRESHOLD = 71/scaleFactor

''' threshold min time after a first rearing to detect the second rearing (frames)'''
SEQUENTIAL_REARING_MIN_TIME_THRESHOLD = 10

''' threshold max time after a first rearing to detect the second rearing (frames)'''
SEQUENTIAL_REARING_MAX_TIME_THRESHOLD = 30

''' threshold for the area around a reared animal for sequential rearing '''
SEQUENTIAL_REARING_POSITION_THRESHOLD = 50

''' threshold for the presence within the water zone '''
MAX_DISTANCE_TO_POINT = 14/scaleFactor

''' threshold to classify the detection as a rearing; height of the front point'''
FRONT_REARING_THRESHOLD = 50

''' threshold to compute head-genital events '''
MAX_DISTANCE_HEAD_HEAD_GENITAL_THRESHOLD = 15

oneFrame = 1
oneSecond = 30
oneMinute = 30*60
oneHour = 30*60*60
oneDay = 30*60*60*24
oneWeek = 30*60*60*24*7


'''time window at the end of an event to test overlap with another event'''
TIME_WINDOW_BEFORE_EVENT = 15*oneFrame


def second( second ):
    return second * oneSecond
    
def day( day ):
    return day* oneDay

def hour( hour ):
    return hour * oneHour