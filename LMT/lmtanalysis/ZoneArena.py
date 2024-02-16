'''
Created by Nicolas Torquet at 14/02/2024
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence
'''


from Parameters import getAnimalTypeParameters


def getZoneCoordinatesFromCornerCoordinatesOpenfieldArea(animalType = None):
    parameters = getAnimalTypeParameters(animalType)
    '''
    parameters contains cornerCoordinatesOpenFieldArea attribute like:
        cornerCoordinatesOpenFieldArea = [
                            (114,63),
                            (398,63),
                            (398,353),
                            (114,353)
                            ]
    '''
    # coordinates of the whole cage: xa = 111, xb = 400, ya = 63, yb = 353
    zoneCoordonates = {
        'xa': parameters.cornerCoordinatesOpenFieldArea[0][0],
        'xb': parameters.cornerCoordinatesOpenFieldArea[2][0],
        'ya': parameters.cornerCoordinatesOpenFieldArea[0][1],
        'yb': parameters.cornerCoordinatesOpenFieldArea[2][1]
    }

    return zoneCoordonates



def getSmallerZoneFromCornerCoordinatesAndMargin(margin, animalType = None):
    '''
    :param margin: in centimeters: has to be converted to pixels
    '''
    parameters = getAnimalTypeParameters(animalType)
    scaleFactor = parameters.scaleFactor
    marginInPixels = margin/scaleFactor
    zoneCoordonates = {
        'xa': parameters.cornerCoordinatesOpenFieldArea[0][0]+marginInPixels,
        'xb': parameters.cornerCoordinatesOpenFieldArea[2][0]-marginInPixels,
        'ya': parameters.cornerCoordinatesOpenFieldArea[0][1]+marginInPixels,
        'yb': parameters.cornerCoordinatesOpenFieldArea[2][1]-marginInPixels
    }
    return zoneCoordonates


def getSmallerZoneFromGivenWholeCageCoordinatesAndMargin(margin, wholeCageCoordinates, animalType = None):
    '''
    :param margin: in centimeters: has to be converted to pixels
    :param wholeCageCoordinates: has to be like {xa = 111, xb = 400, ya = 63, yb = 353}
    '''
    parameters = getAnimalTypeParameters(animalType)
    scaleFactor = parameters.scaleFactor
    marginInPixels = margin/scaleFactor
    zoneCoordonates = {
        'xa': wholeCageCoordinates['xa']+marginInPixels,
        'xb': wholeCageCoordinates['xb']-marginInPixels,
        'ya': wholeCageCoordinates['ya']+marginInPixels,
        'yb': wholeCageCoordinates['yb']-marginInPixels
    }
    return zoneCoordonates


