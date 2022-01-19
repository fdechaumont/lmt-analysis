'''
Created on 24 Septembre 2021

@author: Elodie
'''


from lmtanalysis.Event import *


from lmtanalysis.FileUtil import getFilesToProcess


def process( file ):

    print(file)
    #extract the name of the individual from the name of the file; adjust position!!!
    '''print('ind name: ', file[36:39])
    ind = str(file[36:39])'''
    '''print('ind name: ', file[53:56])
    ind = str(file[53:56])'''
    '''print('ind name: ', file[42:44])
    ind = str(file[42:44])'''

    connection = sqlite3.connect( file )
    
    c = connection.cursor()
    '''query = "UPDATE ANIMAL SET GENOTYPE = 'WT'";
    c.execute(query)'''
    query = "UPDATE ANIMAL SET AGE = '3mo'";
    c.execute( query )
    query = "UPDATE ANIMAL SET SEX = 'male'";
    c.execute( query )
    query = "UPDATE ANIMAL SET STRAIN = '189N3'";
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
    