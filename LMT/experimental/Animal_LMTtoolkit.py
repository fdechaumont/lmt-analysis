'''
Created by Nicolas Torquet at 16/02/2024
torquetn@igbmc.fr
Copyright: CNRS - INSERM - UNISTRA - ICS - IGBMC
CNRS - Mouse Clinical Institute
PHENOMIN, CNRS UMR7104, INSERM U964, Université de Strasbourg
Code under GPL v3.0 licence

Code derived from Animal code
Compatible with LMT-toolkit
'''


from lmtanalysis.Animal import *




class AnimalToolkit(Animal):

    def __init__(self, ID, RFID, NAME=None, GENOTYPE=None, TREATMENT=None, AGE=None, SEX=None, STRAIN=None, SETUP=None,
                 conn=None, animalType=AnimalType.MOUSE):
        self.baseId = ID
        self.RFID = RFID
        self.genotype = GENOTYPE
        self.name = NAME
        self.age = AGE
        self.sex = SEX
        self.strain = STRAIN
        self.setup = SETUP
        self.treatment = TREATMENT
        self.conn = conn
        self.detectionDictionary = {}
        self.parameters = None
        self.setAnimalType(animalType)


    def getTrajectory(self, maskingEventTimeLine=None):
        keyList = sorted(self.detectionDictionary.keys())

        if maskingEventTimeLine != None:
            keyList = maskingEventTimeLine.getDictionary()

        trajectory = {}

        for key in keyList:
            coordinates = self.detectionDictionary.get(key)
            trajectory[key] = (coordinates.massX, -coordinates.massY)

        return trajectory



class AnimalPoolToolkit(AnimalPool):
    """
    Manages an experiment.
    """

    def __init__(self):
        AnimalPool.__init__(self)



    def loadAnimals(self, conn):

        print("Loading animals.")
        cursor = conn.cursor()
        self.conn = conn

        # check experiment parameters

        # Check the number of row available in base
        query = "SELECT * FROM ANIMAL"
        cursor.execute(query)
        field_names = [i[0] for i in cursor.description]
        # print("Fields available in lmtanalysis: ", field_names)

        rows = cursor.fetchall()

        cursor.close()

        self.animalDictionary.clear()
        print("----------------")
        print(type(field_names))
        for row in rows:
            animal = None
            animalPrep = {}
            for index, field in enumerate(field_names):
                animalPrep[field] = row[index]
            animal = AnimalToolkit(**animalPrep, conn=conn)

            if (animal != None):
                self.animalDictionary[animal.baseId] = animal
                print(animal)
            else:
                print("Animal loader : error while loading animal.")

    def getSexList(self):
        sexes = {}

        for k in self.animalDictionary:
            animal = self.animalDictionary[k]
            sexes[animal.sex] = True

        return sexes.keys()