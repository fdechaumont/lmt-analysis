'''
Created on 6 févr. 2025

@author: Fab
'''
from datetime import datetime

class ExperimentManager(object):
    
    '''
    the main experiment is reserved for the main page of the website and does not appear in getExperimentList. Must access it by getExperimentByName("main")
    '''
    
    def __init__(self ):
        
        self.experimentList = []
        
    def addReport(self , report, index = None ):
        print( "addding report " , report )
        
        for experiment in self.experimentList:
            if experiment.name == report.experimentName:
                experiment.addReport( report , index )
                return
        
        # not found, creates it.
        
        experiment = Experiment( report.experimentName )
        experiment.addReport( report, index )
        self.experimentList.append( experiment )
    
    '''
    def insertReport(self, report, index):
        
        for experiment in self.experimentList:
            if experiment.name == report.experimentName:
                experiment.insertReport( report, index )
                return
        
        # not found, creates it.
        
        experiment = Experiment( report.experimentName )
        experiment.insertReport( report, index )
        self.experimentList.append( experiment )
    
    def moveReportIndex( self, sourceIndex, targetIndex, experimentName ):
        
        for experiment in self.experimentList:
            if experiment.name == experimentName:
                experiment.moveReportIndex( sourceIndex, targetIndex )
                return
    '''
    
    def getExperimentList(self):
        l = []
        for experiment in self.experimentList:
            if experiment.name == "main":
                continue
            l.append( experiment )
        return l
        
    
    def getExperimentByName(self, name ):
        for experiment in self.experimentList:
            if experiment.name == name:
                return experiment
        return None
    
    def getAllReports(self):
        reportList = []
        for experiment in self.experimentList:
            reportList.extend( experiment.reportList )
            
        return reportList
    
    def getExperimentListAsNameURL(self):
        l = []
        for experiment in self.experimentList:
            if experiment.name == "main":
                continue            
            l.append( { "name":experiment.simpleName , "url":experiment.url } )
        return l    


class Experiment(object):


    def __init__(self, name ):
        
        self.name = name
        
        self.simpleName = self.name
        
        if "merged" in self.name:
            self.simpleName= self.name[:-7] # remove the -merged at the end of the name of the experiment
        
        self.url = f"exp_{name}.html"
        self.reportList = []
        self.startTime = datetime.now()
        self.endTime = datetime.now()
        
    def addReport(self , report, index = None ):
        
        if index != None:
            self.reportList.insert( index, report )
        else:
            self.reportList.append( report )
            
        self.endTime = datetime.now()

    def insertReport(self , report, index ):
        self.reportList.insert( index, report )
        self.endTime = datetime.now()
    
    def getGenerationTimeInS(self):
        delta = (self.endTime - self.startTime).total_seconds()
        return f"{delta:.1f}"
    
    def __str__(self, *args, **kwargs):
        return f"Experiment {self.name}"
    
    
    
    
    
    
    
    
    
    
    
    
    