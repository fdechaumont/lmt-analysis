'''
Created on 6 sept. 2017

@author: Fab
'''


def getNumberOfIndexOfDatabase( connection ):
    c = connection.cursor()
            
    query = "select type, name, tbl_name, sql FROM sqlite_master WHERE type='index'";
    c.execute( query )
    rows = c.fetchall()
    nbIndex = len( rows )
    print( "Number of index in lmtanalysis: ", nbIndex )
    return nbIndex

def executeLog( cursor, query):
    try:
        print( query )
        cursor.execute( query )
    except Exception as e:
        print (e)
    

def buildDataBaseIndex( connection , force=False):

    print( "Creating lmtanalysis indexes...")

    c = connection.cursor()            

    '''
    if ( force == False ):
        if( getNumberOfIndexOfDatabase( connection ) > 0 ):
            print( "Index already exists (maybe not all)... no re-indexing. Use buildDataBaseIndex force parameter to force index build.")
            return
    '''
     
    executeLog( c , "CREATE INDEX `animalIndex` ON `ANIMAL` (`ID` );" )     

    executeLog( c , "CREATE INDEX `detectionIndex` ON `DETECTION` (`ID` ASC,`FRAMENUMBER` ASC);" )     
        
    executeLog( c , "CREATE INDEX `detetIdIndex` ON `DETECTION` (`ID` ASC);" )     
        
    executeLog( c , "CREATE INDEX `detframenumberIndex` ON `DETECTION` (`FRAMENUMBER` ASC);" )     
        
    executeLog( c , "CREATE INDEX `eventEndFrameIndex` ON `EVENT` (`ENDFRAME` ASC);" )     
        
    executeLog( c , "CREATE INDEX `eventIndex` ON `EVENT` (`ID` ASC,`STARTFRAME` ASC,`ENDFRAME` ASC);" )     

    executeLog( c , "CREATE INDEX `eventStartFrameIndex` ON `EVENT` (`STARTFRAME` ASC);" )     
        
    executeLog( c , "CREATE INDEX `eventstartendIndex` ON `EVENT` (`STARTFRAME` ASC,`ENDFRAME` ASC);" )     
        
    executeLog( c , "CREATE INDEX `indexeventidIndex` ON `EVENT` (`ID` ASC);" )     
    
    executeLog( c , "CREATE INDEX 'detectionFastLoadXYIndex' ON 'DETECTION' ('ANIMALID' ,'FRAMENUMBER' ASC,'MASS_X' ,'MASS_Y' );" )
    
    
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Build DataBase Index" )

        


