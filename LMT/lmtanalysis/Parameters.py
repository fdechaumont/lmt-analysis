'''
Created on 20 dec. 2022

@author: Fab
'''
from lmtanalysis.AnimalType import AnimalType
from lmtanalysis.ParametersMouse import ParametersMouse
from lmtanalysis.ParametersRat import ParametersRat
from lmtanalysis.ParametersHamster import ParametersHamster

def getAnimalTypeParameters( animalType ):

    if animalType == AnimalType.MOUSE:
        return ParametersMouse()

    if animalType == AnimalType.RAT:
        return ParametersRat()
    
    if animalType == AnimalType.HAMSTER:
        return ParametersHamster()

    print("Error: animal type is None")
    quit()
    


    return None