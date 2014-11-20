import re
import sys,unicodedata
import xbmcgui
from sites import furklib
from utils import settings, searcherLib
from ext.hurry.filesize import size
from utils import common

def SearchFromMenu(query):
	dirs = furklib.searchFurk(query)
	for dir in dirs:
		if dir['is_ready']=='0':
			continue
		id = dir['info_hash']
		dirname = dir['name']
		url = sys.argv[0]+'?action=listFiles&id='+id
		common.createListItem(dirname, True, url)
	common.endofDir()
	return

def getMyFiles():
	dirs = furklib.myFiles()
	for dir in dirs:
		if dir['is_ready']=='0':
			continue
		id = dir['info_hash']
		dirname = dir['name']
		url = sys.argv[0]+'?action=listFiles&id='+id
		common.createListItem(dirname, True, url)
	common.endofDir()
	return

def ListFiles(id):
	files = furklib.fileInfo(id)
	for f in files:
		myname = f['name']
		myurl = f['url_dl']
		common.createListItem(myname, False, myurl)
	common.endofDir()
	return

def SearchDialog(type,title,year,season,number,go=False):
	if go:
		updateDialog = xbmcgui.DialogProgress()
		updateDialog.create("Furk Library", "Searching")
		updateDialog.update(20, "searching", title)
	oneclick = settings.getSetting("oneclick")
	if type == 'Show':
		search = searcherLib.ShowSearch(title, season, number, oneclick)
	else:
		search = searcherLib.MovieSearch(title, year, oneclick)

	if len(search.qualities) < 2 and search.oneClickSatisfied == False and search.mediatype=='Show':
			common.Notification('Furk Library 2', 'making a deep search')
			search.deepsearch()
	if search.oneclick:
		if search.oneClickSatisfied:
			common.Notification('Furk Library 2', 'found one click')
			return search.best_quality_result.dir['name'],search.best_quality_result.mediaUrl()
		elif search.best_quality_result:
			common.Notification('Furk Library 2', 'one click not found playing nearest')
			quality_select = 0
		else:
			pass #see what are our options
	if  search.valids > 1 :
		dialog = xbmcgui.Dialog()
        if go: #list items as list item
            for myresult in search.results:
                common.createListItem(myresult.text, False, myresult.mediaUrl())
            common.endofDir()
        else:
		    quality_select = dialog.select('Select quality', search.quality_options())
	elif search.valids == 1:
		common.Notification('Found only:',search.results[0].text.split(' ',1)[0])
		quality_select = 0
	else:
		dialog = xbmcgui.Dialog()
		dialog.ok("Error", "Nothing found", "Try searching in FurkLib Plugin" )
		quality_select = -1
	if quality_select == -1:
		return None,None
	else:
		print 'Quality' + str(quality_select)
		return search.results[quality_select].dir['name'],search.results[quality_select].mediaUrl()


