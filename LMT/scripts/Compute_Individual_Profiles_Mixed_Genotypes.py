'''
Created on 6 sept. 2019

@author: Elodie
'''
import numpy as np
import matplotlib.pyplot as plt


class Mouse:
    
    def __init__(self, rfid, genotype, group ):
        self.rfid = rfid        
        self.genotype = genotype
        self.group = group
        self.event = {}
        self.result = {}        
    
    def propose(self , genotype, event, duration, number ):
        
        nature=""
        if genotype != self.genotype:
            nature = "diff"
        else:
            nature = "same"        
            
        if not (nature,event,"duration") in self.event:
            self.event[(nature,event,"duration")] = 0
            self.event[(nature,event,"number")] = 0
            
        self.event[(nature,event,"duration")]+= duration
        self.event[(nature,event,"number")]+= number
    
    def computeRatio(self):
        
        for e in self.event:
            eventName = e[1]
            diffDuration = self.event[("diff",eventName,"duration")]
            sameDuration = self.event[("same",eventName,"duration")]
            ratio = diffDuration / sameDuration
            self.result[(eventName,"durationRatio")] = ratio

            diffNumber = self.event[("diff",eventName,"number")]
            sameNumber = self.event[("same",eventName,"number")]
            ratio = diffNumber / sameNumber
            self.result[(eventName,"numberRatio")] = ratio
        

if __name__ == '__main__':
    
    dualMouseListRFID = {}
    
    content = ""
    with open("interlab_profiles_night_mixed_genotypes.txt") as f:
        content = f.readlines()
            
        #print(content[2:4])
        
        for nbRow in range(0, len(content)):
            line = content[nbRow]
            
            splitLine = line.split("\t")
    
            nbCol = len( splitLine )
            print("Nb col: " , nbCol)
            
            if nbCol==11:
                nightNumber = int( splitLine[0][-1])
                fileName = splitLine[1]
                indexGroup = fileName.find('_Experiment')
                groupNumber = int ( fileName[indexGroup-2:indexGroup] )
                rfidA = splitLine[2]
                genotypeA = splitLine[3]

                rfidB = splitLine[4]
                genotypeB = splitLine[5]
            
                eventName = splitLine[8]
                duration = int ( splitLine[9] )
                number = int ( splitLine[10] )                
                
                if not rfidA in dualMouseListRFID:
                    dualMouseListRFID[rfidA] = Mouse( rfidA , genotypeA , str ( groupNumber ) )
                    
                mouseA = dualMouseListRFID[rfidA]
                mouseA.propose( genotypeB, eventName, duration, number )
                
                #dual.append( ( nightNumber, indexGroup , rfidA, genotypeA, rfidB, genotypeB, eventName, duration, number ) )
                
                continue
                
            if nbCol==9:
                nightNumber = int( splitLine[0][-1])
                fileName = splitLine[1]
                indexGroup = fileName.find('_Experiment')
                groupNumber = int ( fileName[indexGroup-2:indexGroup] )
                rfid = splitLine[2]
                genotype = splitLine[3]
                eventName = splitLine[6]
                duration = int ( splitLine[7] )
                number = int ( splitLine[8] )
    
                continue
            
            print("Line not recognized")
                

    # question 9:
    
    # question 11:
    # comparer si rgosso modo un J s 'amuse avec une J ou une N ?                

    print( "*************** Result:")
    
    behaviouralEventTwoMice = ["Approach contact", "Approach rear", "Break contact", "Contact", "FollowZone Isolated", "Group2", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way", "Social approach", "Get away", "Train2"]

    for eventName in behaviouralEventTwoMice:

        x = []
        y = []
        color = []
    
        box = {}
    
        for rfid in dualMouseListRFID.keys():
            
            mouse = dualMouseListRFID[rfid]
            mouse.computeRatio()
            print( mouse.genotype, mouse.group )
            #print( mouse.event )
            #print( "duration ratio:" , str( mouse.result[("Contact", "durationRatio")] ) )
            #print( "--")
            
            #ratio = mouse.result[("Contact", "durationRatio")]
            ratio = mouse.result[(eventName, "durationRatio")]
            x.append( mouse.genotype+" duration" )
            y.append( ratio )
            color.append( "blue")

            if not (mouse.genotype+" duration",eventName, "durationRatio") in box:
                box[(mouse.genotype+" duration",eventName, "durationRatio")] = []            
            box[(mouse.genotype+" duration",eventName, "durationRatio")].append( ratio )
            
            ratio = mouse.result[(eventName, "numberRatio")]
            x.append( mouse.genotype+" number" )
            y.append( ratio )
            color.append( "orange")
            
            if not (mouse.genotype+" number",eventName, "numberRatio") in box:
                box[(mouse.genotype+" number",eventName, "numberRatio")] = []            
            box[(mouse.genotype+" number",eventName, "numberRatio")].append( ratio )
            

            
            # y = ratio
            # x = j,n 
        
        # pyplot.boxplot(numpy.array([[1, 2, 3], [2, 7, 8], [1, 3, 10], [2, 5, 12]]))
        
        
        data = []
        labels = []
        for k in box:
            print( k )
            labels.append( k[0] )            
            data.append( (box[k]) )
        print( data )
        plt.boxplot( data , labels = labels )
        
        #plt.scatter(x, y , c=color, alpha = 0.5 )
        
        plt.title(eventName)
        plt.xlabel('condition')
        plt.ylabel('ratio')
        plt.show()
        
    
    
    print("Job done.")