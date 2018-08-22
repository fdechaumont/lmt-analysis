'''
Created on 6 sept. 2017

@author: Fab
'''
from time import *

class Chronometer:
    '''
    classdocs
    '''


    def __init__(self, name):
        '''
        Constructor
        '''
        self.t = time()
        self.name= name
        
    def printTimeInS(self):
        print ( "[Chrono " , self.name , " ] " , self.getTimeInS() , " seconds")
        
    def printTimeInMS(self):
        print ( "[Chrono " , self.name , " ] " , self.getTimeInMS() , " milliseconds")
    
    def getTimeInS(self):
        return time()-self.t
        
    def getTimeInMS(self):
        return ( time()-self.t ) * 1000
        
        
        