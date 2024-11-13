'''
Created on 20 juin 2024

@author: Fab


'''


from socket import *
from lxml import etree
import time
import io
import xml.etree.ElementTree as ET

if __name__ == '__main__':

    '''
    This is an example script that grabs the position x,y of the mice live.
    ( also retreives the hx,hy for head and bx,by for back/bottom )
    
    '''

    #serverName = '192.168.0.143'
    #serverName = '127.0.0.1'
    serverName = '127.0.0.1'
    serverPort = 55044
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    print("connected")
    nb = 0
    while True:
        nb+=1
        retSentence = clientSocket.recv(1024)
        retSentence = retSentence[2:] 
        decode = retSentence.decode() 
        print( decode )
        result = []
        # is XML received ok ? (will crash here if XML is not valid)
        parser = etree.XMLParser(dtd_validation=True)
        
        root = ET.fromstring( decode )
            
        #print ( root )
        for detection in root.iter('detection'):
            result.append( detection.attrib )
        
        print( result )
        
        
    # never reached in this example.
    clientSocket.close()