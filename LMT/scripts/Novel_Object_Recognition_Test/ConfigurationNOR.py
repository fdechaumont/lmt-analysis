'''
#Created on 23 September 2021

#@author: Elodie
'''

import numpy as np

from lmtanalysis.Measure import oneMinute

#object positions (x,y) according to the setup:
objectPosition = {'1': {'left': (190, -152), 'right': (330, -152)},
                  '2': {'left': (192, -152), 'right': (323, -152)},
                    '2i': {'left': (192, -152), 'right': (323, -152)},
                    '2s': {'left': (192, -152), 'right': (323, -152)}
                  }

# object information
objectConfig = {'cc1': {'acquisition': ('cup', 'cup'), 'test': ('cup', 'shaker')},
                'cc2': {'acquisition': ('cup', 'cup'), 'test': ('shaker', 'cup')},
                'ss1': {'acquisition': ('shaker', 'shaker'), 'test': ('shaker', 'cup')},
                'ss2': {'acquisition': ('shaker', 'shaker'), 'test': ('cup', 'shaker')},
                'ff1': {'acquisition': ('falcon', 'falcon'), 'test': ('falcon', 'flask')},
                'ff2': {'acquisition': ('falcon', 'falcon'), 'test': ('flask', 'falcon')},
                'kk1': {'acquisition': ('flask', 'flask'), 'test': ('flask', 'falcon')},
                'kk2': {'acquisition': ('flask', 'flask'), 'test': ('falcon', 'flask')},
                'ck1': {'acquisition': ('cup', 'cup'), 'test': ('cup', 'flask')},
                'ck2': {'acquisition': ('cup', 'cup'), 'test': ('flask', 'cup')},
                'dm1': {'acquisition': ('dice', 'dice'), 'test': ('dice', 'marble')},
                'dm2': {'acquisition': ('dice', 'dice'), 'test': ('marble', 'dice')},
                'kc1': {'acquisition': ('flask', 'flask'), 'test': ('flask', 'cup')},
                'kc2': {'acquisition': ('flask', 'flask'), 'test': ('cup', 'flask')},
                'md1': {'acquisition': ('marble', 'marble'), 'test': ('marble', 'dice')},
                'md2': {'acquisition': ('marble', 'marble'), 'test': ('dice', 'marble')}
                }

organisation = {'short':
                        {'001038125162': 'ff1',
                         '001038125201': 'ff1',
                         '001038125204': 'ff1',
                         '001038125205': 'ff1',
                         '001038125207': 'ff1',
                         '001038125237': 'ff1',
                         '001038125240': 'ff1',
                         '001038125241': 'ff1',
                         '001038125248': 'ff1',
                         '001038125160': 'cc1',
                         '001038125169': 'ff1',
                         '001038125170': 'cc1',
                         '001038125172': 'cc1',
                         '001038125175': 'cc1',
                         '001038125182': 'ff1',
                         '001038125186': 'ff1',
                         '001038125188': 'ff1',
                         '001038125194': 'ff1',
                         '001038125197': 'cc1',
                         '001038125199': 'ff1',
                         '001038125202': 'cc1',
                         '001038125208': 'cc1',
                         '001038125220': 'ff1',
                         '001038125231': 'cc1',
                         '001038125256': 'ff1',
                         '001038125161': 'cc1',
                         '001038125167': 'ff1',
                         '001038125180': 'cc1',
                         '001038125187': 'ff1',
                         '001038125189': 'cc1',
                         '001038125191': 'ff1',
                         '001038125195': 'cc1',
                         '001038125206': 'ff1',
                         '001038125209': 'ff1',
                         '001038125212': 'cc1',
                         '001038125230': 'ff1',
                         '001038125257': 'cc1',
                         '001038125159': 'ff1',
                         '001038125176': 'ff1',
                         '001038125192': 'cc1',
                         '001038125198': 'ff1',
                         '001038125210': 'ff1',
                         '001038125229': 'cc1',
                         '001038125243': 'cc1',
                         '001038125250': 'cc1',
                         '001038125003': 'ff1',
                         '001038125036': 'cc1',
                         '001038125039': 'cc1',
                         '001038125050': 'cc1',
                         '001038125163': 'cc1',
                         '001038125164': 'ff1',
                         '001038125171': 'ff1',
                         '001038125185': 'ff1',
                         '001038125193': 'ff1',
                         '001038125196': 'cc1',
                         '001038125224': 'cc1',
                         '001038125178': 'cc1',
                         '001038125181': 'cc1',
                         '001038125190': 'cc1',
                         '001038125218': 'cc1',
                         '001038125222': 'cc1',
                         '001038125227': 'cc1',
                         '001038125233': 'cc1',
                         '001038125247': 'cc1',
                         '001038125251': 'cc1',
                        '001038125044': 'ff1',
                        '001038125005': 'cc1',
                        '001038124994': 'kk2',
                        '001038125001': 'ss2',
                        '001038125040': 'cc1',
                        '001038125023': 'ff1',
                        '001038124996': 'ss2',
                        '001038125045': 'kk2',
                        '001038125027': 'ff1',
                        '001038125024': 'cc1',
                        '001038124971': 'kk2',
                        '001038125028': 'ss2',
                        '001038125022': 'cc1',
                        '001038124973': 'ff1',
                        '001038124975': 'ff1',
                        '001038124968': 'cc1',
                        '001038125002': 'ss2',
                        '001038125012': 'kk2'
                            },
                'medium':
                    {'001038125162': 'cc1',
                         '001038125201': 'cc1',
                         '001038125204': 'cc1',
                         '001038125205': 'cc1',
                         '001038125207': 'cc1',
                         '001038125237': 'cc1',
                         '001038125240': 'cc1',
                         '001038125241': 'cc1',
                         '001038125248': 'cc1',
                         '001038125160': 'ff1',
                         '001038125169': 'cc1',
                         '001038125170': 'ff1',
                         '001038125172': 'ff1',
                         '001038125175': 'ff1',
                         '001038125182': 'cc1',
                         '001038125186': 'cc1',
                         '001038125188': 'cc1',
                         '001038125194': 'cc1',
                         '001038125197': 'ff1',
                         '001038125199': 'cc1',
                         '001038125202': 'ff1',
                         '001038125208': 'ff1',
                         '001038125220': 'cc1',
                         '001038125231': 'ff1',
                         '001038125256': 'cc1',
                         '001038125161': 'ff1',
                         '001038125167': 'cc1',
                         '001038125180': 'ff1',
                         '001038125187': 'cc1',
                         '001038125189': 'ff1',
                         '001038125191': 'cc1',
                         '001038125195': 'ff1',
                         '001038125206': 'cc1',
                         '001038125209': 'cc1',
                         '001038125212': 'ff1',
                         '001038125230': 'cc1',
                         '001038125257': 'ff1',
                         '001038125159': 'cc1',
                         '001038125176': 'cc1',
                         '001038125192': 'ff1',
                         '001038125198': 'cc1',
                         '001038125210': 'cc1',
                         '001038125229': 'ff1',
                         '001038125243': 'ff1',
                         '001038125250': 'ff1',
                         '001038125003': 'cc1',
                         '001038125036': 'ff1',
                         '001038125039': 'ff1',
                         '001038125050': 'ff1',
                         '001038125163': 'ff1',
                         '001038125164': 'cc1',
                         '001038125171': 'cc1',
                         '001038125185': 'cc1',
                         '001038125193': 'cc1',
                         '001038125196': 'ff1',
                         '001038125224': 'ff1',
                         '001038125178': 'ff1',
                         '001038125181': 'ff1',
                         '001038125190': 'ff1',
                         '001038125218': 'ff1',
                         '001038125222': 'ff1',
                         '001038125227': 'ff1',
                         '001038125233': 'ff1',
                         '001038125247': 'ff1',
                         '001038125251': 'ff1',
                     '001038125044': 'cc2',
                    '001038125005': 'ff2',
                    '001038124994': 'cc1',
                    '001038125001': 'kk1',
                    '001038125040': 'ff2',
                    '001038125023': 'ss2',
                    '001038124996': 'ff1',
                    '001038125045': 'cc1',
                    '001038125027': 'cc2',
                    '001038125024': 'kk2',
                    '001038124971': 'cc1',
                    '001038125028': 'kk1',
                    '001038125022': 'ff2',
                    '001038124973': 'cc2',
                    '001038124975': 'cc2',
                    '001038124968': 'ff2',
                    '001038125002': 'ff1',
                    '001038125012': 'ss1'
                    },
                'long':
                    {'M01': 'dm1', 'M02': 'kc1','M03': 'dm2','M04': 'kc2','M05': 'ck1',
                     'M06': 'md1', 'M07': 'md2','M08': 'ck2','M09': 'dm1','M10': 'kc1',
                     'M11': 'dm2','M12': 'kc2','M13': 'md1','M14': 'ck1','M15': 'md2',
                     'M16': 'ck2','M17': 'dm1','M18': 'kc1','M19': 'dm2','M20': 'kc2',
                     'M21': 'md1', 'M22': 'ck1','M23': 'md2',
                     
                     '189N3-F34': 'ff1','189N3-F38': 'cc1','189N3-F72': 'ss1','189N3-F73': 'kk1','189N3-F39': 'ff2','189N3-F44': 'ss2','189N3-F45': 'cc2','189N3-F46': 'kk1','189N3-F11': 'ff1','189N3-F12': 'cc2','189N3-F21': 'ss1','189N3-F22': 'kk2','189N3-F65': 'ff2','189N3-F67': 'ss2','189N3-F52': 'cc1','189N3-F62': 'kk1','189N3-F116': 'ff1','189N3-F117': 'ss2','189N3-F118': 'cc1','189N3-F119': 'kk2'
                     
},
#'189N3-14': 'dm1','189N3-15': 'md1','189N3-16': 'md1', '189N3-17': 'md1','189N3-18': 'dm2','189N3-19': 'dm1','189N3-20': 'md2','189N3-29': 'dm2','189N3-42': 'md1','189N3-60': 'md2','189N3-11': 'dm2','189N3-21': 'md2','189N3-22': 'dm1','189N3-38': 'md2','189N3-39': 'dm1','189N3-44': 'md1','189N3-45': 'dm1','189N3-46': 'dm2','189N3-52': 'md2','189N3-62': 'dm2','189N3-65': 'md1','189N3-67': 'dm1','189N3-72': 'md2','189N3-73': 'dm2'
                'longIso':
                    {'M01': 'md1',
                     'M02': 'dm1',
                     'M03': 'md1',
                     'M04': 'dm1',
                     'M05': 'dm2',
                     'M06': 'md2',
                     'M07': 'dm2',
                     'M08': 'md2',
                     'M09': 'md1',
                     'M10': 'dm1',
                     'M11': 'md1',
                     'M12': 'dm1',
                     'M13': 'dm2',
                     'M14': 'md2',
                     'M15': 'dm2',
                     'M16': 'md2',
                     'M17': 'md1',
                     'M18': 'dm1',
                     'M19': 'md1',
                     'M20': 'dm1',
                     'M21': 'dm2',
                     'M22': 'md2',
                     'M23': 'dm2'
                     }
                }


radiusObjects = {'cup': 18, 'flask': 15, 'falcon': 9, 'shaker': 11, 'marble': 7, 'dice': 6}
colorObjects = {'cup': 'gold', 'flask': 'mediumpurple', 'falcon': 'mediumseagreen', 'shaker': 'orchid', 'marble': 'royalblue', 'dice': 'red'}
objectList = ['cup', 'flask', 'falcon', 'shaker', 'marble', 'dice']

mutantGeno = 'Del/+'
#mutantGeno = 'Tg+'
#mutantGeno = 'KO'

colorSap = {'WT': 'dodgerblue', mutantGeno: 'darkorange', '1': 'dodgerblue', '2': 'red'}

# sexList = ['male', 'female']
sexList = ['M', 'F']
#sexList = ['female']
#genoList = ['WT', 'Del/+']
genoList = ['WT', mutantGeno]
configList = ['config1', 'config2']
setupList = ['2i', '2s']
setupList = ['1', '2']

markerList = {'1': 'o', '2': 'v', '2i': 'v', '2s': 'o'} #for the setups
markerListConfig = {'config1': 'o', 'config2': 'v'} #for the setups
markerListSex = {'male': 'v', 'female': 'o'}

# xPos = {'male': {setupList[0]: 1.5, setupList[1]: 4.5},
#         'female': {'1': 1.5, '2': 4.5}}
# xPosConfig = {'male': {'config1': 1.5, 'config2': 4.5},
#         'female': {'config1': 7.5, 'config2': 10.5}}

xPos = {'M': {setupList[0]: 1.5, setupList[1]: 4.5},
        'F': {'1': 1.5, '2': 4.5}}
xPosConfig = {'M': {'config1': 1.5, 'config2': 4.5},
        'F': {'config1': 7.5, 'config2': 10.5}}

#VIBRISSAE = 3 #estimated size of the vibrissae to determine the contact zone with the object
timeBin = 1 * oneMinute

eventList = {'acquisition': ['SniffLeftFar', 'SniffRightFar', 'SniffLeft', 'SniffRight', 'UpLeft', 'UpRight'], 'test': ['SniffFamiliarFar', 'SniffNewFar', 'SniffFamiliar', 'SniffNew', 'UpFamiliar', 'UpNew']}
colorEvent = {'SniffLeft': 'dodgerblue', 'SniffRight': 'darkorange', 'SniffLeftFar': 'navy', 'SniffRightFar': 'gold', 'UpLeft': 'skyblue', 'UpRight': 'peachpuff',
                          'SniffFamiliar': 'mediumseagreen', 'SniffNew': 'blueviolet', 'SniffFamiliarFar': 'darkgreen', 'SniffNewFar': 'magenta', 'UpFamiliar': 'lightgreen', 'UpNew': 'violet'}


def getStartTestPhase(pool):
    cursor = pool.conn.cursor()
    query = "SELECT FRAMENUMBER, PAUSED FROM FRAME"
    try:
        cursor.execute(query)
    except:
        print("can't access data for PAUSED")

    rows = cursor.fetchall()
    cursor.close()

    frameNumberList = []

    for row in rows:
        pauseValue = row[1]
        if pauseValue == 1:
            frameNumberList.append(row[0])
    sortedFrameList = sorted(frameNumberList)

    lastPausedFrame = sortedFrameList[-1]
    startFrameTestPhase = lastPausedFrame + 1
    return startFrameTestPhase

def getColorGeno(geno):
    if geno == 'WT':
        color = 'steelblue'
    else:
        color = 'darkorange'
    return color


def getColorSetup(setup):
    if setup == '1':
        color = 'royalblue'
    elif setup == '2':
        color = 'red'
    elif setup == '2i':
        color = 'steelblue'
    elif setup == '2s':
        color = 'green'
    elif setup == '4':
        color = 'darkgreen'
    return color

def getColorStrain(strain):
    if strain == 'C57BL6J':
        color = 'royalblue'
    elif strain == 'BTBR':
        color = 'red'
    elif strain == 'Long Evans':
        color = 'royalblue'
    elif strain == 'Sprague Dawley':
        color = 'darkorange'
    return color

def getColorConfig(config):
    if config == 'config1':
        color = 'steelblue'
    else:
        color = 'darkorange'
    return color

def getConfigCat(rfid, exp, organisation):
    config = 'None'
    configName = organisation[exp][rfid]
    if 'md' in configName:
        config = 'config1'
    elif 'dm' in configName:
        config = 'config1'
    elif 'kc' in configName:
        config = 'config2'
    elif 'ck' in configName:
        config = 'config2'
    elif 'ff' in configName:
        config = 'config1'
    elif 'kk' in configName:
        config = 'config1'
    elif 'ss' in configName:
        config = 'config2'
    elif 'cc' in configName:
        config = 'config2'
    return config
