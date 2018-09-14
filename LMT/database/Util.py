'''
Created on 6 sept. 2017

@author: Fab
'''

def level( data ):
    dico = {}
    for entry in data:
        dico[entry]=True
    return sorted( dico.keys( ) )        
        

def pixelToCm( nbPixel ):
    return nbPixel * 10 / 57        
        
def getMinTMaxTAndFileNameInput():
    
    tmin = int ( input("tMin : ") )
    tmax = int ( input("tMax : ") )
    text_file_name = input("File name : ")
    text_file_name = text_file_name+".txt"
    text_file = open ( text_file_name, "w")
    
    return tmin,tmax,text_file

def convert_to_d_h_m_s( frames ):
    """Return the tuple of days, hours, minutes and seconds."""
    seconds = frames / 30
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    return days, hours, minutes, seconds    
