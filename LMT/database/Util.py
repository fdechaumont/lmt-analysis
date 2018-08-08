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

