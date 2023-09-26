'''
Created on 29 ao�t 2018

@author: Fab
'''


import glob
from tkinter.dialog import Dialog
from tkinter.filedialog import askopenfilename, askdirectory
import tkinter as tk
import unittest
from random import randrange, random
import json



'''
Provide a dialog to ask for either files or folder to process.
In case of folder, this use glob to recursively get all .sqlite files in sub folders.
'''
def getFilesToProcess():


    root = tk.Tk()
    root.withdraw()
    root.update()

    d = Dialog(
        title="Select input for processing", text="Select file(s) or folder for processing", bitmap = 'question',
        strings=('Files', 'Folder', 'Cancel'), default=0 )

    root.focus_force()
    files = None    
    if(  d.num == 0 ):
        files = askopenfilename( title="Choose a set of file to process", multiple=1, filetypes = (("sqlite files","*.sqlite"),("all files","*.*") )  )

    if ( d.num == 1):
        
        folder = askdirectory( title= "Choose a directory to process")
        print ("Folder: " , folder )
        folder = folder+"/**/*.sqlite"
        print( "Fetching files...")
        files = []
        for file in glob.glob( folder, recursive=True ):
            print( file , "found.")
            files.append( file )
    
    d.destroy()
    root.destroy()
    
    return files


def getJsonFileToProcess():
    root = tk.Tk()
    root.withdraw()
    root.update()

    d = Dialog(
        title="Select json file for processing", text="Select file for processing", bitmap='question',
        strings=('File', 'Cancel'), default=0)

    root.focus_force()
    file = None
    if (d.num == 0):
        file = askopenfilename(title="Choose a file to process", multiple=0,
                                filetypes=(("json files", "*.json"), ("all files", "*.*")))

    d.destroy()
    root.destroy()

    return file


def getJsonFilesToProcess():
    root = tk.Tk()
    root.withdraw()
    root.update()

    d = Dialog(
        title="Select input for processing", text="Select file(s) or folder for processing", bitmap='question',
        strings=('Files', 'Folder', 'Cancel'), default=0)

    root.focus_force()
    files = None
    if (d.num == 0):
        files = askopenfilename(title="Choose a set of file to process", multiple=1,
                                filetypes=(("json files", "*.json"), ("all files", "*.*")))

    if (d.num == 1):

        folder = askdirectory(title="Choose a directory to process")
        print("Folder: ", folder)
        folder = folder + "/**/*.json"
        print("Fetching files...")
        files = []
        for file in glob.glob(folder, recursive=True):
            print(file, "found.")
            files.append(file)

    d.destroy()
    root.destroy()

    return files


def getJsonFilesWithSpecificNameToProcess( namePartIncluded ):
    root = tk.Tk()
    root.withdraw()
    root.update()

    d = Dialog(
        title="Select input for processing", text="Select folder for processing", bitmap='question',
        strings=('Folder', 'Cancel'), default=0)

    root.focus_force()

    folder = askdirectory(title="Choose a directory to process")
    print("Folder: ", folder)
    folder = folder + "/**/*.json"
    print("Fetching files...")
    files = []
    for file in glob.glob(folder, recursive=True):
        if namePartIncluded in file:
            print(file, "found.")
            files.append(file)

    d.destroy()
    root.destroy()

    return files

def getCsvFileToProcess():
    root = tk.Tk()
    root.withdraw()
    root.update()

    d = Dialog(
        title="Select csv file for processing", text="Select csv file for processing", bitmap='question',
        strings=('File', 'Cancel'), default=0)

    root.focus_force()
    file = None
    if (d.num == 0):
        file = askopenfilename(title="Choose a csv file to process", multiple=0,
                                filetypes=(("csv files", "*.csv"), ("all files", "*.*")))

    d.destroy()
    root.destroy()

    return file


def mergeJsonFilesForProfiles(files):
    #initiate the result dictionary with the keys of one example file
    resultsDic = {}

    for jsonFile in files:
        print(jsonFile)
        # upload json file:
        with open(jsonFile) as json_data:
            data = json.load(json_data)
        print("json file re-imported.")

        resultsDic = {**resultsDic, **data}
    
    print(resultsDic.keys())
    
    return resultsDic

def addJitter(x, jit):
    newX = []
    for item in x:
        addedJitter = (random() * 2 - 1) * jit
        newX.append(item + addedJitter)

    return newX


def extractPValueFromLMMResult( result, keyword ):
    r = result.summary().as_text()
    for l in r.split("\n"):
        if keyword in l:
            print (l)
            lineWithoutSpace = ' '.join(l.split())
            pValue = float( lineWithoutSpace.split(" ")[4] )
            sign = 1
            print( "test: " , lineWithoutSpace.split(" ")[1] )
            if float( lineWithoutSpace.split(" ")[1] ) < 0:
                sign=-1
            print ( "P VALUE :" , pValue )
            print ( "SIGN :" , sign )
            return pValue, sign

def getFigureBehaviouralEventsLabelsFrench(event):
    behaviouralEventsLabels = {"Stop isolated": 'repos isole',
                         "Move isolated": 'mouvement isole',
                         "Break contact": 'rupture de contact',
                         "Get away": 'echappement',
                         "Social approach": 'approche',
                         # "Approach rear": 'approach reared mouse',
                         "Approach contact": 'approche avant contact',
                         "Contact": 'contact',
                         "Oral-oral Contact": 'nez-nez',
                         "Oral-genital Contact": 'nez-anogenital',
                         "Side by side Contact": 'cote-a-cote',
                         "Side by side Contact, opposite way": 'cote-a-cote, tete beche',
                         "seq oral oral - oral genital": 'nez-nez & nez-anogenital',
                         "seq oral geni - oral oral": 'nez-anogenital & nez-nez',
                         "FollowZone Isolated": 'poursuite',
                         "FollowZone": 'poursuite',
                         "Train2": 'train2'
                         # , "longChase": 'long chase'
                         }
    return behaviouralEventsLabels[event]

def getFigureBehaviouralEventsLabels(event):
    behaviouralEventsLabels = {
                        'totalDistance': 'distance',
                        "Stop isolated": 'single idle',
                         "Move isolated": 'single move',
                         "Move in contact": 'move in contact',
                         "WallJump": 'jumps',
                         "Rear isolated": 'rearing',
                         "Rear in contact": 'rearing in contact',
                         "Break contact": 'break contact',
                         "Get away": 'get away',
                         "Social approach": 'approach social range',
                         #"Approach rear": 'approach reared mouse',
                         "Approach contact": 'approach contact',
                         "Contact": 'contact',
                         "Group2": 'group of 2', 
                         "Group3": 'group of 3', 
                         "Oral-oral Contact": 'nose-nose',
                         "Oral-genital Contact": 'nose-anogenital',
                         "Side by side Contact": 'side-side',
                         "Side by side Contact, opposite way": 'side-side, head-to-tail',
                         "seq oral oral - oral genital": 'nose-nose & nose-anogenital',
                         "seq oral geni - oral oral": 'nose-anogenital & nose-nose',
                         "FollowZone Isolated": 'follow0',
                         "FollowZone": 'follow',
                         "Train2": 'train2',
                         "Group 3 make": 'make group 3',
                         "Group 4 make": 'make group 4',
                         "Break contact": 'break contact',
                         "Group 3 break": 'break group 3',
                         "Group 4 break": 'break group 4',
                         
                         'Oral-oral Contact exclusive': 'nose-nose (x)',
                           'Side by side Contact exclusive': 'side-side (x)',
                           'Oral-genital Contact exclusive': 'nose-anogenital (x)',
                           'Passive oral-genital Contact exclusive': 'passive nose-anogenital (x)',
                           'Side by side Contact, opposite way exclusive': 'side-side head-to-tail (x)',
                           'Oral-oral and Side by side Contact exclusive': 'nose-nose & side-side (x)',
                           'Oral-genital and Side by side Contact, opposite way exclusive': 'nose-anogenital & side-side head-to-tail (x)',
                           'Oral-genital passive and Side by side Contact, opposite way exclusive':
                               'passive nose-anogenital & side-side head-to-tail (x)', 'Other contact exclusive': 'other contacts (x)',
                           'Move isolated exclusive': 'single move (x)',
                           'Stop isolated exclusive': 'single idle (x)',
                           'Undetected exclusive': 'undetected (x)'
                         # , "longChase": 'long chase'
                         }
    
    return behaviouralEventsLabels[event]





behaviouralEventOneMouse = ["Move isolated", "Move in contact", "Stop isolated", "Rear isolated", "Rear in contact",
    "Contact", "Group2", "Group3", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way",
    "Train2", "FollowZone",
    "Social approach", "Approach contact",
    "Group 3 make", "Group 4 make", "Break contact",
    "Group 3 break", "Group 4 break"
    ]

behaviouralEventOneMouseDic = {' TotalLen': ["Move isolated", "Move in contact", "Stop isolated", "Rear isolated", "Rear in contact",
    "Contact", "Group2", "Group3", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way",
    "Train2", "FollowZone"],
    
    ' Nb': ["Move isolated", "Move in contact", "Stop isolated", "Rear isolated", "Rear in contact",
    "Contact", "Group2", "Group3", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way",
    "Train2", "FollowZone",
    "Approach contact",
    "Group 3 make", "Group 4 make", "Break contact",
    "Group 3 break", "Group 4 break"],
    
    ' MeanDur': ["Move isolated", "Move in contact", "Stop isolated", "Rear isolated", "Rear in contact",
    "Contact", "Group2", "Group3", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way",
    "Train2", "FollowZone",
    "Approach contact",
    "Break contact"
    ]
    }

behaviouralEventOneMousePairDic = {' TotalLen': ["Move isolated", "Move in contact", "Stop isolated", "Rear isolated", "Rear in contact",
    "Oral-genital Contact", 
    "Train2", "FollowZone"],
    
    ' Nb': ["Move isolated", "Move in contact", "Stop isolated", "Rear isolated", "Rear in contact",
    "Oral-genital Contact", 
    "Train2", "FollowZone",
    "Approach contact",
    "Break contact"
    ],
    
    ' MeanDur': ["Move isolated", "Move in contact", "Stop isolated", "Rear isolated", "Rear in contact",
    "Oral-genital Contact", 
    "Train2", "FollowZone",
    "Approach contact",
    "Break contact"
    ]
    }

behaviouralEventOneMousePairSymetricDic = {' TotalLen': ['Contact', 'Oral-oral Contact', "Side by side Contact", "Side by side Contact, opposite way"],
    
    ' Nb': ['Contact', 'Oral-oral Contact', "Side by side Contact", "Side by side Contact, opposite way"],
    
    ' MeanDur': ['Contact', 'Oral-oral Contact', "Side by side Contact", "Side by side Contact, opposite way"]
    }

behaviouralEventOneMouseSingle = ["Move isolated", "Move in contact", "Stop isolated", "Rear isolated", "Rear in contact", "Oral-genital Contact", "Train2", "FollowZone",
                                "Social approach", "Approach contact", "Break contact"]
behaviouralEventOneMouseSocial = ["Contact", "Group2", "Oral-oral Contact", "Oral-genital Contact",
                            "Side by side Contact", "Side by side Contact, opposite way",
                            "Train2", "FollowZone",
                            "Social approach", "Approach contact",
                            "Break contact"]

categoryList = [' TotalLen', ' Nb', ' MeanDur']

unitCatDic = {' TotalLen': 's', ' Nb': 'nb', ' MeanDur': 's'}

def getBehaviouralEventName(behavEvent, cat):
    if behavEvent != 'totalDistance':
        event = behavEvent + cat

    elif behavEvent == 'totalDistance':
        event = behavEvent
        
    return event

def getBehaviouralTraitsPerCategory(category):
    listBehavioursOfInterest = []
    if category == 'activity': #10
        listBehavioursOfInterest = ['Move isolated TotalLen', 'Move isolated Nb', 'Move isolated MeanDur', 
                                             'Move in contact TotalLen', 'Move in contact Nb', 'Move in contact MeanDur',
                                             'Stop isolated TotalLen', 'Stop isolated Nb', 'Stop isolated MeanDur',
                                             'totalDistance']
    if category == 'exploration': #6
        listBehavioursOfInterest = ['Rear isolated TotalLen', 'Rear isolated Nb', 'Rear isolated MeanDur',
                                    'Rear in contact TotalLen', 'Rear in contact Nb', 'Rear in contact MeanDur']
    
    if category == 'activity & exploration': #13
        listBehavioursOfInterest = ['totalDistance', 'Move isolated TotalLen', 'Move isolated Nb', 'Move isolated MeanDur', 
                                             'Move in contact TotalLen', 'Move in contact Nb', 'Move in contact MeanDur',
                                             'Stop isolated TotalLen', 'Stop isolated Nb', 'Stop isolated MeanDur',
                                             'Rear isolated TotalLen', 'Rear isolated Nb', 'Rear isolated MeanDur']

    if category == 'contacts': #21
        listBehavioursOfInterest = ["Contact TotalLen", "Contact Nb", "Contact MeanDur", 
                                    "Group2 TotalLen", "Group2 Nb", "Group2 MeanDur", 
                                    "Group3 TotalLen", "Group3 Nb", "Group3 MeanDur", 
                                    "Oral-oral Contact TotalLen", "Oral-oral Contact Nb", "Oral-oral Contact MeanDur", 
                                    "Oral-genital Contact TotalLen", "Oral-genital Contact Nb", "Oral-genital Contact MeanDur", 
                                    "Side by side Contact TotalLen", "Side by side Contact Nb", "Side by side Contact MeanDur", 
                                    "Side by side Contact, opposite way TotalLen", "Side by side Contact, opposite way Nb", "Side by side Contact, opposite way MeanDur"]
    
    if category == 'specific contacts': #12
        listBehavioursOfInterest = ["Oral-oral Contact TotalLen", "Oral-oral Contact Nb", "Oral-oral Contact MeanDur", 
                                    "Oral-genital Contact TotalLen", "Oral-genital Contact Nb", "Oral-genital Contact MeanDur", 
                                    "Side by side Contact TotalLen", "Side by side Contact Nb", "Side by side Contact MeanDur", 
                                    "Side by side Contact, opposite way TotalLen", "Side by side Contact, opposite way Nb", "Side by side Contact, opposite way MeanDur"]
    
    
    if category == 'general contacts': #9
        listBehavioursOfInterest = ["Contact TotalLen", "Contact Nb", "Contact MeanDur", 
                                    "Group2 TotalLen", "Group2 Nb", "Group2 MeanDur", 
                                    "Group3 TotalLen", "Group3 Nb", "Group3 MeanDur"]
            
    if category == 'follow': #6
        listBehavioursOfInterest = ["Train2 TotalLen", "Train2 Nb", "Train2 MeanDur", 
                                    "FollowZone TotalLen", "FollowZone Nb", "FollowZone MeanDur"]
        
    if category == 'approach': #4
        listBehavioursOfInterest = ["Approach contact Nb", "Approach contact MeanDur", "Group 3 make Nb", "Group 4 make Nb" ]
        
    if category == 'escape': #4
        listBehavioursOfInterest = ["Break contact Nb", "Break contact MeanDur", "Group 3 break Nb", "Group 4 break Nb"]
    
    if category == 'follow, approach & escape': #14
        listBehavioursOfInterest = ["Train2 TotalLen", "Train2 Nb", "Train2 MeanDur", 
                                    "FollowZone TotalLen", "FollowZone Nb", "FollowZone MeanDur",
                                    "Approach contact Nb", "Approach contact MeanDur", "Group 3 make Nb", "Group 4 make Nb",
                                    "Break contact Nb", "Break contact MeanDur", "Group 3 break Nb", "Group 4 break Nb" ]
        
    return listBehavioursOfInterest

def getBehaviouralTraitsPerCategoryForPCA(category):
    listBehavioursOfInterest = []
    if category == 'activity': #11
        listBehavioursOfInterest = ['Move isolated TotalLen', 'Move isolated Nb',  
                                             'Move in contact TotalLen', 'Move in contact Nb', 
                                             'Stop isolated TotalLen', 'Stop isolated Nb', 
                                             'totalDistance', 'Rear isolated TotalLen', 'Rear isolated Nb',
                                    'Rear in contact TotalLen', 'Rear in contact Nb']

    if category == 'social': #26
        listBehavioursOfInterest = ["Contact TotalLen", "Group2 TotalLen", "Group3 TotalLen", "Oral-oral Contact TotalLen", "Oral-genital Contact TotalLen", "Side by side Contact TotalLen", "Side by side Contact, opposite way TotalLen",
                                    "Contact Nb", "Group2 Nb", "Group3 Nb", "Oral-oral Contact Nb", "Oral-genital Contact Nb", "Side by side Contact Nb", "Side by side Contact, opposite way Nb",
                                    "Train2 TotalLen", "FollowZone TotalLen",
                                    "Train2 Nb", "FollowZone Nb",
                                    "Approach contact Nb", "Group 3 make Nb", "Group 4 make Nb", "Approach contact MeanDur",
                                    "Break contact Nb", "Group 3 break Nb", "Group 4 break Nb", "Break contact MeanDur"]
    
    if category == 'contacts': #14
        listBehavioursOfInterest = ["Contact TotalLen", "Group2 TotalLen", "Group3 TotalLen", "Oral-oral Contact TotalLen", "Oral-genital Contact TotalLen", "Side by side Contact TotalLen", "Side by side Contact, opposite way TotalLen",
                                    "Contact Nb", "Group2 Nb", "Group3 Nb", "Oral-oral Contact Nb", "Oral-genital Contact Nb", "Side by side Contact Nb", "Side by side Contact, opposite way Nb"]
        
    if category == 'social dynamic': #12
        listBehavioursOfInterest = ["Train2 TotalLen", "FollowZone TotalLen",
                                    "Train2 Nb", "FollowZone Nb",
                                    "Approach contact Nb", "Group 3 make Nb", "Group 4 make Nb", "Approach contact MeanDur",
                                    "Break contact Nb", "Group 3 break Nb", "Group 4 break Nb", "Break contact MeanDur"]
        
    return listBehavioursOfInterest


class TestFileUtil ( unittest.TestCase ):
    
    def test_fillBetween(self):

        files = getFilesToProcess()
        for file in files:
            print ( file )
        
        self.assertEqual( True, True )