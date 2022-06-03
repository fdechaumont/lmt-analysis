'''
Created on 23 Feb. 2022

@author: Elodie
'''


exclusiveEventList = ['Oral-oral Contact exclusive', 'Side by side Contact exclusive', 'Oral-genital Contact exclusive',
                       'Passive oral-genital Contact exclusive', 'Side by side Contact, opposite way exclusive',
                       'Oral-oral and Side by side Contact exclusive',
                       'Oral-genital and Side by side Contact, opposite way exclusive',
                       'Oral-genital passive and Side by side Contact, opposite way exclusive', 'Other contact exclusive', 'Move isolated exclusive', 'Stop isolated exclusive', 'Undetected exclusive']

contactTypeList = ["Oral-oral Contact", "Oral-genital Contact", "Passive oral-genital Contact", "Side by side Contact", "Side by side Contact, opposite way", "Other contact"]

exclusiveEventsLabels = {'Oral-oral Contact exclusive': 'N-N', 'Side by side Contact exclusive': 'S-S', 'Oral-genital Contact exclusive': 'N-G',
                       'Passive oral-genital Contact exclusive': 'N-G pass', 'Side by side Contact, opposite way exclusive': 'S-S opp',
                       'Oral-oral and Side by side Contact exclusive': 'N-N S-S',
                       'Oral-genital and Side by side Contact, opposite way exclusive': 'N-G S-S opp',
                       'Oral-genital passive and Side by side Contact, opposite way exclusive': 'N-G pass S-S opp', 'Other contact exclusive': 'other',
                        'Move isolated exclusive': 'move', 'Stop isolated exclusive': 'idle', 'Undetected exclusive': 'undetected'}

exclusiveEventListLabels = [exclusiveEventsLabels[x] for x in exclusiveEventList]

sexList = ['male', 'female']
mutantGeno = 'Del/+'
genoList = ['WT', mutantGeno]

genoListGeneral = ['{}-{}'.format(genoList[0], genoList[0]), '{}-{}'.format(genoList[0], genoList[1]),
                   '{}-{}'.format(genoList[1], genoList[1])]
sexListGeneral = ['{}-{}'.format(sexList[0], sexList[0]), '{}-{}'.format(sexList[0], sexList[1]),
                  '{}-{}'.format(sexList[1], sexList[1])]
