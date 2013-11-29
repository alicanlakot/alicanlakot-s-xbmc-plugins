import re
import sys,unicodedata
from sites import furklib
from utils import settings,searchLib
from ext.hurry.filesize import size
from utils import common

quality_options = []
quality_urls = []
quality_cleanname =[]
quality_ids =[]
quality_values =[]
unquality_options = []
unquality_urls = []
unquality_cleanname =[]
unquality_ids =[]
unquality_values =[]
unique_qualities = []



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




	if len(unique_qualities)<=2 and type=='Show':


		season_episode = "s%.2de%.2d" % (int(season), int(number))
		season_episode2 = "%d%.2d" % (int(season), int(number))

		tv_show_season = "%s season" % (title)
		tv_show_episode = "%s %s" % (title, season_episode)

		dirs2 = []
		dirs2.extend(furklib.myFiles(title))
		try:
			dirs2.extend(furklib.searchFurk(tv_show_episode))
		except:
			pass
		try:
			dirs2.extend(furklib.searchFurk(tv_show_season))
		except:
			pass
		try:
			dirs2.extend(furklib.searchFurk(title))
		except:
			pass

	        #files = remove_list_duplicates(files)

		# dirs2 = files
		titletoCheck = re.sub(r'\([^)]*\)', '', title)
		titletoCheck = common.CleanFileName(titletoCheck).lower()

		dir_names = []
		dir_ids = []

		if go:
			pDialog = xbmcgui.DialogProgress()
			pDialog.create('Searching for files')

		count = 0

		for d in dirs2:

			count = count + 1
			percent = int(float(count * 100) / len(dirs2))
			text = "%s files found ->" % len(quality_options)
			for qual in unique_qualities:
				text = text + qual +','
				if go:
					pDialog.update(percent, text)
					if pDialog.iscanceled():
						pDialog.close()
		        		break

			if d['is_ready']=='0':
				continue


			dirnametoCheck=common.CleanFileName(d['name']).lower()
			print 'title:'+titletoCheck
			print 'dirname:'+dirnametoCheck
			if dirnametoCheck.startswith(titletoCheck) and 'season' in dirnametoCheck and str(season) in dirnametoCheck:
				print 'filebyfile for:'+dirnametoCheck
				filebyfile(d['info_hash'],d['name'],title,year,season,number)


		for d in dirs2:
			if len(quality_options)>0:
				continue
			if d['is_ready']=='0':
				continue
			if not (d['name'].lower().startswith(title.lower())):
				continue
			dir_names.append(d['name'])
			dir_ids.append(d['info_hash'])


		if len(dir_names)>0:
			idx = 0
			for dirname in dir_names:
				id = dir_ids[idx]
				idx = idx + 1
				filebyfile(id,dirname,title,year,season,number)
		else:
			pass

	if go:
		pDialog.close()

	oneclick = settings.getSetting("oneclick")

	if len(quality_options)==0 and len(unquality_options)>0:
		oneclick = False
		dialog = xbmcgui.Dialog()
		dialog.ok("Error", "Nothing of good quality", "Making a similar search" )
		quality_options = unquality_options
		quality_cleanname = unquality_cleanname
		quality_urls = unquality_urls
		quality_ids= unquality_ids
		quality_values = unquality_values

	if len(quality_options) > 1 :
		if oneclick:
	            quality_select = -1
	            j,k = getQualitysetting()
    		    best_quality = 0
		    i = 0
	            for myoption in quality_options:
		        if quality_values[i] >= j and quality_values[i] < k:
			    quality_select= i
	                    break
			else:
				if quality_values[i] > best_quality and quality_values[i] < j:
					best_quality = quality_values[i]
					quality_select = i
	            i= i + 1

		if quality_select == -1:
			dialog = xbmcgui.Dialog()
	                dialog.ok("Error", "Nothing of one click quality", "Please select yourself" )
		        dialog = xbmcgui.Dialog()
			quality_select = dialog.select('Select quality', quality_options)

	elif len(quality_options) == 1:
		common.Notification('Found only:',quality_options[0].split(' ',1)[0])
		quality_select = 0
	else:
		quality_select = -1

	if len(quality_options)==0:
		dialog = xbmcgui.Dialog()
		dialog.ok("Error", "Nothing found", "Try searching in FurkLib Plugin" )

	# common.Notification ('Selected' , str(quality_select))
	if quality_select == -1:
		return None,None
	else:
		if type=='Show':

			try:
				myurl = quality_urls[quality_select]
				if myurl:
					myname = quality_cleanname[quality_select]
				else:
					raise Exception("empty url")
			except:
				myid = quality_ids[quality_select]
				files = furklib.fileInfo(myid)
				k = k +1
				for f in files:
					myname = f['name']
					#print myname
					if 'sample' in myname.lower():
						continue
					if myname.endswith('avi') or myname.endswith('mkv') or myname.endswith('mp4'):
						myurl = f['url_dl']
						break
					else:
						continue
		elif type=='Movie':
				myid = quality_ids[quality_select]
				files = furklib.fileInfo(myid)
				myurl = None
				for f in files:
					myname = f['name'].lower()
					#print myname
					if 'sample' in myname:
						continue
					if myname.endswith('avi') or myname.endswith('mkv') or myname.endswith('mp4') or myname.endswith('iso'):
						myurl = f['url_dl']
						myname = f['name']
						break
					else:
						continue



		#common.Notification('Found',myname)
		if myurl:
			return myname,myurl
		else:
			common.Notification('Not Found' , 'Please try again')
			return None,None


def listfiles(id):
	files = furklib.fileInfo(id)
	for f in files:
		myname = f['name']
		if 'sample' in myname.lower() or 'subs' in myname.lower():
			continue
		play_url = f['url_dl']
		if myname.endswith('avi') or myname.endswith('mkv') or myname.endswith('mp4') or myname.endswith('iso'):
			quality_options.append(myname)
			quality_cleanname.append(myname)
			quality_urls.append(play_url)

	return
