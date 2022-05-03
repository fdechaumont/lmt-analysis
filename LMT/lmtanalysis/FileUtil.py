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
                         "Train2": 'train2'
                         # , "longChase": 'long chase'
                         }
    return behaviouralEventsLabels[event]


class TestFileUtil ( unittest.TestCase ):
    
    def test_fillBetween(self):

        files = getFilesToProcess()
        for file in files:
            print ( file )
        
        self.assertEqual( True, True )