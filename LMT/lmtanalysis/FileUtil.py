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

def addJitter(x, jit):
    newX = []
    for item in x:
        addedJitter = (random() * 2 - 1) * jit
        newX.append(item + addedJitter)

    return newX


def getStarsFromPvalues(pvalue, numberOfTests):
    stars = "ns"

    s1 = 0.05 / numberOfTests
    s2 = 0.01 / numberOfTests
    s3 = 0.001 / numberOfTests

    if pvalue < s3:
        stars = "***"
    if pvalue >= s3 and pvalue < s2:
        stars = "**"
    if pvalue >= s2 and pvalue < s1:
        stars = "*"

    return stars


class TestFileUtil ( unittest.TestCase ):
    
    def test_fillBetween(self):

        files = getFilesToProcess()
        for file in files:
            print ( file )
        
        self.assertEqual( True, True )