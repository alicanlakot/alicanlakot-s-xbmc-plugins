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
	if type == 'Show':
		search = searcherLib.ShowSearch(title, season, number, True)
	else:
		search = searcherLib.MovieSearch(title, year, True)
	if settings.getSetting("oneclick") == True and type =='Show':
		searchResult = search.oneClickResult()
		return searchResult.text,searchResult.mediaUrl()


#===============================================================================
# 	if len(unique_qualities)<=2 and type=='Show':
#
#
# 		season_episode = "s%.2de%.2d" % (int(season), int(number))
# 		season_episode2 = "%d%.2d" % (int(season), int(number))
#
# 		tv_show_season = "%s season" % (title)
# 		tv_show_episode = "%s %s" % (title, season_episode)
#
# 		dirs2 = []
# 		dirs2.extend(furklib.myFiles(title))
# 		try:
# 			dirs2.extend(furklib.searchFurk(tv_show_episode))
# 		except:
# 			pass
# 		try:
# 			dirs2.extend(furklib.searchFurk(tv_show_season))
# 		except:
# 			pass
# 		try:
# 			dirs2.extend(furklib.searchFurk(title))
# 		except:
# 			pass
#
# 	        #files = remove_list_duplicates(files)
#
# 		# dirs2 = files
# 		titletoCheck = re.sub(r'\([^)]*\)', '', title)
# 		titletoCheck = common.CleanFileName(titletoCheck).lower()
#
# 		dir_names = []
# 		dir_ids = []
#
# 		if go:
# 			pDialog = xbmcgui.DialogProgress()
# 			pDialog.create('Searching for files')
#
# 		count = 0
#
# 		for d in dirs2:
#
# 			count = count + 1
# 			percent = int(float(count * 100) / len(dirs2))
# 			text = "%s files found ->" % len(quality_options)
# 			for qual in unique_qualities:
# 				text = text + qual +','
# 				if go:
# 					pDialog.update(percent, text)
# 					if pDialog.iscanceled():
# 						pDialog.close()
# 		        		break
#
# 			if d['is_ready']=='0':
# 				continue
#
#
# 			dirnametoCheck=common.CleanFileName(d['name']).lower()
# 			print 'title:'+titletoCheck
# 			print 'dirname:'+dirnametoCheck
# 			if dirnametoCheck.startswith(titletoCheck) and 'season' in dirnametoCheck and str(season) in dirnametoCheck:
# 				print 'filebyfile for:'+dirnametoCheck
# 				filebyfile(d['info_hash'],d['name'],title,year,season,number)
#
#
# 		for d in dirs2:
# 			if len(quality_options)>0:
# 				continue
# 			if d['is_ready']=='0':
# 				continue
# 			if not (d['name'].lower().startswith(title.lower())):
# 				continue
# 			dir_names.append(d['name'])
# 			dir_ids.append(d['info_hash'])
#
#
# 		if len(dir_names)>0:
# 			idx = 0
# 			for dirname in dir_names:
# 				id = dir_ids[idx]
# 				idx = idx + 1
# 				filebyfile(id,dirname,title,year,season,number)
# 		else:
# 			pass
#
# 	if go:
# 		pDialog.close()
#
# 	oneclick = settings.getSetting("oneclick")
#
# 	if len(quality_options)==0 and len(unquality_options)>0:
# 		oneclick = False
# 		dialog = xbmcgui.Dialog()
# 		dialog.ok("Error", "Nothing of good quality", "Making a similar search" )
# 		quality_options = unquality_options
# 		quality_cleanname = unquality_cleanname
# 		quality_urls = unquality_urls
# 		quality_ids= unquality_ids
# 		quality_values = unquality_values
#===============================================================================
	search.fillOptions()
	if  len(search.results) > 1 :
		dialog = xbmcgui.Dialog()
		quality_select = dialog.select('Select quality', search.quality_options())

	elif len(search.results) == 1:
		common.Notification('Found only:',search.results[0].text.split(' ',1)[0])
		quality_select = 0
	else:
		quality_select = -1

	if len(search.results) ==0:
		dialog = xbmcgui.Dialog()
		dialog.ok("Error", "Nothing found", "Try searching in FurkLib Plugin" )

	# common.Notification ('Selected' , str(quality_select))
	if quality_select == -1:
		return None,None
	else:
		print 'Quality' + str(quality_select)
		return search.results[quality_select].file['name'],search.results[quality_select].mediaUrl()


