import xbmcgui
import re
import sys,unicodedata
from sites import furklib
from utils import common,settings
from ext.titles.series import SeriesParser
from ext.titles.movie import MovieParser
from ext.titles.parser import TitleParser, ParseWarning
from ext.hurry.filesize import size

quality_options = []
quality_urls = []
quality_cleanname =[]
quality_ids =[]
unquality_options = []
unquality_urls = []
unquality_cleanname =[]
unquality_ids =[]
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

def SearchDialog(type,title,year,season,number):
	global quality_options
	global quality_urls
	global quality_cleanname 
	global quality_ids
	global unquality_options
	global unquality_urls
	global unquality_cleanname
	global unquality_ids
	global unique_qualities

	updateDialog = xbmcgui.DialogProgress()
        updateDialog.create("Furk Library", "Searching")
	updateDialog.update(20, "searching", title)	
	
	dialog = xbmcgui.Dialog()
	title = common.CleanFileName(title)

	if type=='Movie':
		if year==0:
			query = '{0} -cam'.format(title)
			dirs = furklib.searchFurk(query)
		else:
			query = '{0} {1} -cam'.format(title,year)
			dirs = furklib.searchFurk(query)
	elif type=='Show':

		query = '''{0} S{1:0>2}E{2:0>2}'''.format(title, season, number)
		dirs = furklib.searchFurk(query)
	else:
		query = title
		dirs = furklib.searchFurk(title)

	updateDialog.close()
	k = 0
	found720p = False
	foundDvd = False
	pDialog = xbmcgui.DialogProgress()
	pDialog.create('Searching for files')
	count = 0

	if dirs:
		for file in dirs:
			count = count + 1
			percent = int(float(count * 100) / len(dirs))
			text = "%s files found ->" % len(quality_options) 
			for qual in unique_qualities:
				text = text + qual +','
			pDialog.update(percent, text)
			if pDialog.iscanceled(): 
				pDialog.close()
				break

			if file['is_ready']=='0':
				continue
			id = file['info_hash']
			dirname = file['name']
			mysize = size(int(file['size']))
			valid = False

			#print ('Dirname ' + dirname)
			dirname = common.CleanFileName(dirname)
			

			if type=='Show':
				

				myParser= guess_series(dirname)
				if myParser:
					print 'my parser is ok'
					myParser.parse()
					myName = myParser.name 
					mySeason = myParser.season
					myNumber = myParser.episode
					myYear = 0
					myNametoCheck = common.CleanFileName(myName).lower().replace(' ','')
					titletoCheck = common.CleanFileName(title).lower().replace(' ','')
					if myParser.quality: myquality = myParser.quality
					movie_name = '''{0} {1} S{2:0>2}E{3:0>2}'''.format(myquality,myNametoCheck, mySeason, myNumber)
					if int(mySeason) <> int(season):
						print 'break'
						break
					elif titletoCheck == myNametoCheck and int(mySeason)==int(season) and int(myNumber)==int(number) and myquality.value>0:
						valid= True
		
				
					
					#Notification(mycheck.lower(),query.lower())
					if valid:
						#Notification('Quality:',str(myquality))
						quality_options.append('[' + mysize + '] '+str(myquality) + ' ' + dirname)
						quality_ids.append(file['info_hash'])
						quality_cleanname.append(dirname)
						quality_urls.append(None)
						if not str(myquality) in unique_qualities:
							unique_qualities.append(str(myquality))
				else:
					# Notification ('cannot parse' , dirname)
					continue
	
			elif type=='Movie':
				valid = False
				parser = MovieParser()
				parser.data = dirname
				parser.parse()
				myName = parser.name 
				myYear = parser.year
				myquality = parser.quality
				movie_name =  str(myquality) + ' ' + dirname
				movie_name2 = str(myquality) + ' ' + title.strip() + ' (' + str(year) + ')'
			
				if year==0 and title.lower() in myName.lower():
					valid = True
				if not myYear:
					myYear = 0
					valid = False
				title = unicodedata.normalize('NFKD',unicode(title,'utf-8')).encode('ASCII', 'ignore')
				#print 'T:' + title.lower()
				#print 'M:' + myName.lower() 
				if title.lower() in myName.lower() and myquality.value>250:
					valid = True

				if valid:
					quality_options.append('[' + mysize + '] '+ movie_name)
					quality_cleanname.append(dirname)
					quality_ids.append(file['info_hash'])
					if not str(myquality) in unique_qualities:
						unique_qualities.append(str(myquality))
					
				else:
					unquality_options.append(str(myquality) + ' ' + dirname)
					unquality_ids.append(file['info_hash'])
					unquality_cleanname.append(dirname)

			

	if len(unique_qualities)<=2 and type=='Show':
		

		season_episode = "s%.2de%.2d" % (int(season), int(number))
		season_episode2 = "%d%.2d" % (int(season), int(number))
	
		tv_show_season = "%s season" % (title)
		tv_show_episode = "%s %s" % (title, season_episode)

		dirs2 = []
		dirs2.extend(furklib.searchFurk(tv_show_episode))
	        dirs2.extend(furklib.searchFurk(tv_show_season))
		dirs2.extend(furklib.searchFurk(title)) 
	        #files = remove_list_duplicates(files)

		# dirs2 = files
		titletoCheck = re.sub(r'\([^)]*\)', '', title)
		titletoCheck = common.CleanFileName(titletoCheck).lower()

		dir_names = []
		dir_ids = []
		
		pDialog = xbmcgui.DialogProgress()
		pDialog.create('Searching for files')
	        count = 0

		for d in dirs2:
			
			count = count + 1
		        percent = int(float(count * 100) / len(dirs2))
			text = "%s files found ->" % len(quality_options) 
			for qual in unique_qualities:
				text = text + qual +','

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
					
		
		if len(dir_names)>0 and len(dir_names)<2:
			idx = 0
			for dirname in dir_names:
				id = dir_ids[idx]
				idx = idx + 1 
				filebyfile(id,dirname,title,year,season,number)

		elif len(dir_names)>7 or len(quality_options)==0:
			dir_names = []
			dir_ids = []
			for d in dirs2:
				if d['is_ready']=='0':
					continue
				dir_names.append(d['name'])
				dir_ids.append(d['info_hash'])

			dir_select = dialog.select('Select directory', dir_names)
			id = dir_ids[dir_select]
			dirname = dir_names[dir_select]
			filebyfile(id,dirname,title,year,season,number)
			if len(quality_options)==0:
				listfiles(id)
		else:
			pass

		
	pDialog.close()

	if len(quality_options)==0 and len(unquality_options)>0:
		dialog = xbmcgui.Dialog()	
		dialog.ok("Error", "Nothing of good quality", "Making a similar search" )	
		quality_options = unquality_options
		quality_cleanname = unquality_cleanname
		quality_urls = unquality_urls
		quality_ids= unquality_ids
	

        if len(quality_options) > 1 :       
		quality_select = dialog.select('Select quality', quality_options)
	elif len(quality_options)==1:
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
		return myname,myurl

def guess_series(title):
        """Returns a valid series parser if this :title: appears to be a series"""
        #print 'title=' + title.encode("utf-8")
        parser = SeriesParser(identified_by='ep', allow_seasonless=False)
        # We need to replace certain characters with spaces to make sure episode parsing works right
        # We don't remove anything, as the match positions should line up with the original title
        clean_title = re.sub('[_.,\[\]\(\):]', ' ', title)
        match = parser.parse_episode(clean_title)
        if match:
            if parser.parse_unwanted(clean_title):
                return
            elif match['match'].start() > 1:
                # We start using the original title here, so we can properly ignore unwanted prefixes.
                # Look for unwanted prefixes to find out where the series title starts
                start = 0
                prefix = re.match('|'.join(parser.ignore_prefixes), title)
                if prefix:
                    start = prefix.end()
                # If an episode id is found, assume everything before it is series name
                name = title[start:match['match'].start()]
                # Remove possible episode title from series name (anything after a ' - ')
                name = name.split(' - ')[0]
                # Replace some special characters with spaces
                name = re.sub('[\._\(\) ]+', ' ', name).strip(' -')
                # Normalize capitalization to title case
                name = name.title()
                # If we didn't get a series name, return
                if not name:
                    return
                parser.name = name
                parser.data = title
		
                try:
                    parser.parse(data=title)
                except ParseWarning, pw:
                    common.Notification('ParseWarning:' , pw.value)
                if parser.valid:
                    return parser

def filebyfile(id,dirname,title,year,season,number):
		global quality_options
		global quality_urls
		global quality_cleanname 
		global quality_ids
		global unquality_options
		global unquality_urls
		global unquality_cleanname
		global unquality_ids
		global unique_qualities

		valid = False
		title = re.sub(r'\([^)]*\)', '', title)
		titletoCheck = common.CleanFileName(title).lower().replace(' ','')

		#print 'Dir:{0}'.format(dirname)
		files = furklib.fileInfo(id)

		for f in files:
			name = f['name']
			path = f['path'].replace('/',' ')
			mysize = size(int(f['size']))
			if 'sample' in name.lower() or 'subs' in name.lower():
				continue
			play_url = f['url_dl']
			valid = False
			myquality = 'unknown Akin'
			myParser= guess_series(name)
			if not myParser:
				myParser= guess_series(title + ' ' + name)
			if not myParser:
				myParser= guess_series(title + ' ' + path + name)
			movie_name = dirname + ' ' + path + name
			if myParser:
				try:
					myParser.parse()
				except:
					continue
				myName = myParser.name 
				mySeason = myParser.season
				myNumber = myParser.episode
				myYear = 0
				if myParser.quality: myquality = myParser.quality
				myNametoCheck = common.CleanFileName(myName).lower().replace(' ','')
				
				movie_name = '''{0} {1} S{2:0>2}E{3:0>2}'''.format(myquality,myName, mySeason, myNumber)
				movie_name2 = '''B:{0} {1} S{2}E{3}'''.format('unk',title, season, number)
				clean_name = '''{1} S{2:0>2}E{3:0>2}'''.format(myquality,myName, mySeason, myNumber)
				#print 'U: {0} S{1}E{2}'.format(myNametoCheck,mySeason,myNumber)
				#print 'Y: {0} S{1}E{2}'.format(titletoCheck,season,number)
				if not myNametoCheck.startswith(titletoCheck):
					#print 'break namecheck'
					break
				if int(mySeason)==int(season) and int(myNumber)==int(number):
					valid= True
	
			if valid:
				quality_options.append('[' + mysize + '] '+str(myquality) + ' ' + name)
				quality_cleanname.append(clean_name)
				quality_urls.append(play_url)
				if not str(myquality) in unique_qualities:
					unique_qualities.append(str(myquality))
				break
			else:
				unquality_options.append('[' + mysize + '] '+movie_name)
				unquality_cleanname.append(movie_name)
				unquality_urls.append(play_url)
		return

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
			