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
        


