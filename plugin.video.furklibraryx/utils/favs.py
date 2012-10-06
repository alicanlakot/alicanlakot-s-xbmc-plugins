import os,sys
import urllib
from utils import filehelpers
from utils import common

FAVOURITES_FILE = sys.modules[ "__main__" ].FAVOURITES_FILE


def favs_menu():
    if not os.path.isfile(FAVOURITES_FILE):
        return
    
    items = []
    s = filehelpers.read_from_file(FAVOURITES_FILE)
    menu_items = s.split('\n')
    
    for menu_item in menu_items:
        if len(menu_item) < 3:
            break
        data = menu_item.split('\t')
        item_name = data[0]
        item_url = data[1]
	isFolder= data[2]
        
	common.createfavItem(item_name,isFolder,urllib.unquote(item_url))


    common.endofDir()

def addtoFavs(name, mode,isFolder):
    if favs_index(name, mode, isFolder) >= 0:
        return
    content = str(name) + '\t' + str(mode) + '\t' + str(isFolder) + '\n'
    filehelpers.write_to_file(FAVOURITES_FILE, content, append=True)
    
    
def removefromFavs(name, mode,isFolder):
    index = favs_index(name, mode,isFolder)
    print index
    if index >= 0:
        content = filehelpers.read_from_file(FAVOURITES_FILE)
        lines = content.split('\n')
        lines.pop(index)
        s = ''
        for line in lines:
            if len(line) > 0:
                s = s + line + '\n'
        
        if len(s) == 0:
            os.remove(FAVOURITES_FILE)
        else:
            filehelpers.write_to_file(FAVOURITES_FILE, s)

def favs_index(name, mode,isFolder):
    try:
        content = filehelpers.read_from_file(FAVOURITES_FILE)
        line = str(name) + '\t' + str(mode) + '\t' + str(isFolder)
        lines = content.split('\n')
        index = lines.index(line)
        return index
    except:
        return -1 #Not subscribed

