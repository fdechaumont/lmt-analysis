'''
Created on 24 Septembre 2021

@author: Elodie
'''


from lmtanalysis.Event import *


from lmtanalysis.FileUtil import getFilesToProcess


def process( file ):

    print(file)
    #extract the name of the individual from the name of the file; adjust position!!!
    '''print('ind name: ', file[15:18])
    ind = str(file[15:18])'''
    '''print('ind name: ', file[89:92])
    ind = str(file[89:92])'''
    '''print('ind name: ', file[42:44])
    ind = str(file[42:44])'''

    connection = sqlite3.connect( file )
    
    c = connection.cursor()
    query = "UPDATE ANIMAL SET GENOTYPE = 'Del/+'";
    c.execute(query)
    query = "UPDATE ANIMAL SET AGE = '14we'";
    c.execute( query )
    query = "UPDATE ANIMAL SET SEX = 'female'";
    c.execute( query )
    query = "UPDATE ANIMAL SET STRAIN = 'B6C3B17p21.31'";
    c.execute( query )
    query = "UPDATE ANIMAL SET SETUP = '2'";
    c.execute(query)
    '''query = "UPDATE ANIMAL SET NAME = '189N3-{}'".format(ind);
    c.execute(query)
    query = "UPDATE ANIMAL SET RFID = '189N3-{}'".format(ind);
    c.execute(query)'''

    connection.commit()
    c.close()
    connection.close()

    

def processAll():
    
    
    files = getFilesToProcess()

    chronoFullBatch = Chronometer("Full batch" )    
        
    if ( files != None ):
    
        for file in files:
                print ( "Processing file" , file )
                process( file )
        
    chronoFullBatch.printTimeInS()
    print( "*** ALL JOBS DONE ***")

if __name__ == '__main__':
    
    print("Code launched.")
    processAll()
    