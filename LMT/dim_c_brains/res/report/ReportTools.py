'''
Created on 18 févr. 2025

@author: Fab

code from https://gist.github.com/wassname/1393c4a57cfcbf03641dbc31886123b8

'''

import unicodedata
import string

valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
char_limit = 200

colors = [
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf'   # blue-teal
    ]

def clean_filename(filename, whitelist=valid_filename_chars, replace=' '):
    # replace spaces
    for r in replace:
        filename = filename.replace(r,'_')
    
    # keep only valid ascii chars
    cleaned_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode()
    
    # keep only whitelisted chars
    cleaned_filename = ''.join(c for c in cleaned_filename if c in whitelist)
    if len(cleaned_filename)>char_limit:
        print("Warning, filename truncated because it was over {}. Filenames may no longer be unique".format(char_limit))
    return cleaned_filename[:char_limit] 



def getAnimalReportColor( animal, animalList ):
    animalList = sorted ( animalList )
    
    return colors[ animalList.index( animal )]

def getAnimalReportColorMap( animalList ):
    animalList = sorted ( animalList )
    _map = {}
    for animal in animalList:
        _map[animal] = getAnimalReportColor(animal, animalList)
    return _map

if __name__ == '__main__':
    pass