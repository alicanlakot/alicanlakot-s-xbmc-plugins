'''
    Furk.net player for XBMC
    Copyright (C) 2010 Gpun Yog 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys, re, time, os, shutil
import urllib,urllib2
import xbmc,xbmcgui,xbmcplugin,xbmcaddon
import getter,printer

from resources.lib.utils.titles.series import SeriesParser
from resources.lib.utils.titles.movie import MovieParser
from resources.lib.utils.titles.parser import TitleParser, ParseWarning
from resources.lib.BeautifulSoup import BeautifulSoup


#import feedparser

__settings__ = sys.modules[ "__main__" ].__settings__
ADDON = xbmcaddon.Addon(id='plugin.video.furklibrary')
##MOVIES_PATH= os.path.join('C:/Users/altasak/XBMC/movies','')
##TV_SHOWS_PATH = os.path.join('C:/Users/altasak/XBMC/shows2','')
if ADDON.getSetting('movie_custom_directory') == "true":
	MOVIES_PATH = ADDON.getSetting('movie_directory')
else:
	MOVIES_PATH = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.furklibrary/movies'), '')

if ADDON.getSetting('tv_show_custom_directory') == "true":
	TV_SHOWS_PATH = ADDON.getSetting('tv_show_directory')
else:
	TV_SHOWS_PATH = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.furklibrary/tvshows'), '')

OTHERS_PATH = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.furklibrary/others'), '')
HISTORY_FILE = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.furklibrary'), 'history.txt')
		
def AddOption(text, isFolder, mode, name=''):
	li = xbmcgui.ListItem(text)
	url = sys.argv[0]+'?action=' + str(mode) + '&name='+ name
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)

def AddonMenu():  #homescreen
	print 'FurkLibrary menu'
	#AddOption('Run',False, 'AU')
	#AddOption('MovieLens',True, 'movielens')
	#AddOption('Search',True,'recent_queries&query=')
	#AddOption('Delete History and Dirs',False, 'DeleteHistory')
	#AddOption('About',False, 'about')
	AddOption('This plugin is no more supported',False, 'about')
	AddOption('Please add Furk Library 2 from Alicanlakots Repository',False, 'about')
	text = 'Click here to try automatically'
	li = xbmcgui.ListItem(text)
	url = 'plugin://plugin.video.furklibrary2/'+'?action=none' 
	xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=True)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def addFiles(did,dirname,files):
	if not files:
                return
	total = len(files)
	scraped = 0
	for f in files:
                id = f.getElementsByTagName('id').item(0).firstChild.data
                name = f.getElementsByTagName('name').item(0).firstChild.data
                print name.encode("utf-8")
                play_url = f.getElementsByTagName('url').item(0).firstChild.data
                dirname = dirname.replace("/","")
                strmfilename,mypath = nameCheck(name,dirname)
                if mypath:
                        url = sys.argv[0] + '?action=playMe&did=' + did + '&fid=' + id + '&name="' + strmfilename + '"'
                        CreateStreamFile(strmfilename,url,mypath,False)
                        scraped = scraped+1
        return scraped

def addFiles2(did,targetdir,files):
	if not files:
                return
	total = len(files)
	scraped = 0
	for f in files:
                id = f.getElementsByTagName('id').item(0).firstChild.data
                name = f.getElementsByTagName('name').item(0).firstChild.data
                p = re.compile('[-._ \\/]sample[-._ \\/]', re.I)
                m = p.search(name)
                if m:
                        continue
                else:
                        pass
                play_url = f.getElementsByTagName('url').item(0).firstChild.data
                strmfilename = CleanFileName(name,False)
                url = sys.argv[0] + '?action=playMe&did=' + did + '&fid=' + id + '&name="' + strmfilename + '"'
                CreateStreamFile(strmfilename,url,targetdir,False)
                scraped = scraped+1
        return scraped


                
def playMe(did,fid):
        return playMe(did,fid,'')
        
def playMe(did,fid,name):
        ##Notification("Navigating to ",name)
        files = getter.getFiles(did)
        found= False
        if files:
                for f in files:
                        id = f.getElementsByTagName('id').item(0).firstChild.data
                        name = f.getElementsByTagName('name').item(0).firstChild.data
                        play_url = f.getElementsByTagName('url').item(0).firstChild.data
                        if (id == fid):
                                found = True
                                return play_url
                               

        
        if not found:
                return None
                #dialog = xbmcgui.Dialog()
                #quality_select = dialog.select('Select quality', dirs[0].getElementsByTagName('name').item(0).firstChild.data)
                #mydisplay = MyClass()
                #mydisplay.doModal()
                #del mydisplay
                                
        
                

def getFeed(url):
        d = feedparser.parse(url)
        for entry in d['entries']:
                print entry.title
                propername,dummy = nameCheck(entry.title,'')
                dirs= getter.searchDirs(propername)
                d= dirs[0]
                if d:
                        id = d.getElementsByTagName('id').item(0).firstChild.data
                        name = d.getElementsByTagName('name').item(0).firstChild.data
                        date = d.getElementsByTagName('date').item(0).firstChild.data
                        thumb = d.getElementsByTagName('thumb').item(0).firstChild.data
                        files = getter.getFiles(id)
                        printer.addFiles(files)
                        
def DeleteHistory():
	dialog = xbmcgui.Dialog()
	if dialog.yesno("Remove", "Do you want to remove history file?"):
		print "Removing history.txt"
		try:
			os.remove(HISTORY_FILE)
		except:
                        pass
                try:
			RemoveDirectory(MOVIES_PATH)
			RemoveDirectory(TV_SHOWS_PATH)
			RemoveDirectory(OTHERS_PATH)
			xbmc.executebuiltin('CleanLibrary(video)')
		except:
			Notification("Error during remove of directories")

def SetupAutoUpdate():
	source_path = os.path.join(xbmc.translatePath('special://profile/'), 'autoexec.py')
	try:
		file = open(source_path, 'r')
		content=file.read()
		file.close()
		index = content.find("import time;time.sleep(5);xbmc.executebuiltin(\"XBMC.RunScript(special://home/addons/plugin.video.furklibrary/default.py,0,action='AU')\")")
		if index > 0:
			Notification("Already set up", "Auto update is already set up in autoexec.py")
			return
	except:
		content = "import xbmc\n"
	content += "\nimport time;time.sleep(5);xbmc.executebuiltin(\"XBMC.RunScript(special://home/addons/plugin.video.furklibrary/default.py,0,action='AU')\")"
	
	file = open(source_path, 'w')
	file.write(content)
	file.close()
	print "autoexec.py updated to include IceFilms auto update"
	dialog = xbmcgui.Dialog()	
	dialog.ok("Auto update added to autoexec.py", "To complete the setup:", " 1) Activate auto update in IceLibrary configs.", " 2) Restart XBMC.")	

            
def nameCheck(name,dirname):
                
         # Check here from the name if this is a series or not
                p = re.compile('[-._ \\/]sample[-._ \\/]', re.I)
                m = p.search(name)
                if m:
                        print 'm:' + name.encode("utf-8")
                        return None,None
                else:
                        pass
                myParser= guess_series(name)
                
                #xbmcgui.Dialog().ok('ok')
                if myParser:
                        myParser.parse()
                        show_name= myParser.name
                        episode= str(myParser.episode).zfill(2)
                        
                        season = str(myParser.season).zfill(2)
                        show_path = os.path.join(TV_SHOWS_PATH, CleanFileName(show_name, False))
                        CreateDirectory(show_path)		
                        season_path = os.path.join(show_path, season)
                        CreateDirectory(season_path)
                        show_full = show_name + ' S' + season + 'E' + str(episode)
                        return show_full,season_path
                        

                else:
                        parser = MovieParser()
                        parser.data = name
                        parser.parse()
                        myName = parser.name 
                        myYear = parser.year
                        myotherspath = os.path.join(OTHERS_PATH, dirname)
                        print 'myName=' + myName.encode("utf-8")
                        print 'Year=' + str(myYear)
                        if myName:
                                        print 'my name exists'
                                        if myYear:
                                                print 'myyear exists'
                                                myquality = parser.quality
                                                movie_name = myName + ' (' + str(myYear) + ') ' + myquality
                                                dirname = CleanFileName(dirname,False)
                                                mydir= os.path.join(MOVIES_PATH , myquality)
                                                print 'name =' + name.encode("utf-8")
                                                print 'myquality=' + myquality
                                                if myquality=="xyz":
                                                        CreateDirectory(myotherspath)
                                                        return movie_name,myotherspath
                                                else:
                                                        print 'Movie Dir being created'
                                                        CreateDirectory(mydir)
                                                        return movie_name,mydir
                                                
                                        else:
                                                print name.encode("utf-8")
                                                CreateDirectory(myotherspath)
                                                return myName,myotherspath
                        return None,None


def nameCheck2(name):
                print 'oldname=' + name.encode("utf8")
                name = name.replace('[ www.Speed.Cd ] - ','')
                name = name.replace('[ UsaBit.com ] - ','')
                print 'newname=' + name.encode("utf8")
         # Check here from the name if this is a series or not
                myParser= guess_series(name)
                
                #xbmcgui.Dialog().ok('ok')
                if myParser:
                        print 'Show'
                        myParser.parse()
                        show_name= myParser.name
                        episode= str(myParser.episode).zfill(2)
                        season = str(myParser.season).zfill(2)
                        show_path = os.path.join(TV_SHOWS_PATH, CleanFileName(show_name, False))
                        CreateDirectory(show_path)		
                        season_path = os.path.join(show_path, season)
                        CreateDirectory(season_path)
                        show_full = show_name + ' S' + season + 'E' + str(episode)
                        return season_path
                        

                else:
                        parser = MovieParser()
                        parser.data = name
                        parser.parse()
                        myName = parser.name 
                        myYear = parser.year
                        myotherspath = os.path.join(OTHERS_PATH, CleanFileName(name,False))
                        print 'myName=' + myName.encode("utf-8")
                        print 'Year=' + str(myYear)
                        if myName:
                                        print 'my name exists'
                                        if myYear:
                                                print 'myyear exists'
                                                myquality = parser.quality
                                                movie_name = myName + ' (' + str(myYear) + ')'
                                                mydir= os.path.join(MOVIES_PATH , myquality ,movie_name)
                                                print 'name =' + name.encode("utf-8")
                                                print 'myquality=' + myquality
                                                if myquality=="xyz":
                                                        CreateDirectory(myotherspath)
                                                        return myotherspath
                                                else:
                                                        print 'Movie Dir being created'
                                                        CreateDirectory(mydir)
                                                        return mydir
                                                
                                        else:
                                                print name.encode("utf-8")
                                                CreateDirectory(myotherspath)
                                                return myotherspath
                        return None



                
def CreateStreamFile(name, href, dir, remove_year):
	try:
		CreateDirectory(dir)
		strm_string = href.encode("utf-8")
		filename = CleanFileName(name, remove_year) + ".strm"
		path = os.path.join(dir, filename)
		file = open(path,'w')
		file.write(strm_string)
		file.close()
	except:
		Notification("Error while creating strm file for : " , name)
        

def CleanFileName(s, remove_year):
	if remove_year:
		s = s[0:len(s)-7]
	s = s.replace(' (Eng subs)', '')
	s = s.replace(' (eng subs)', '')
	s = s.replace(' (English subs)', '')
	s = s.replace(' (english subs)', '')
	s = s.replace(' (Eng Subs)', '')
	s = s.replace(' (English Subs)', '')
	s = s.replace('&#x26;', '&')
	s = s.replace('&#x27;', '\'')
	s = s.replace('&#xC6;', 'AE')
	s = s.replace('&#xC7;', 'C')
	s = s.replace('&#xF4;', 'o')
	s = s.replace('&#xE9;', 'e')
	s = s.replace('&#xEB;', 'e')
	s = s.replace('&#xED;', 'i')
	s = s.replace('&#xEE;', 'i')
	s = s.replace('&frac12;', ' ')
	s = s.replace('&#xBD;', ' ') #half character
	s = s.replace('&#xB3;', ' ')
	s = s.replace('&#xB0;', ' ') #degree character
	s = s.replace('&#xA2;', 'c')
	s = s.replace('&#xE2;', 'a')
	s = s.replace('&#xEF;', 'i')
	s = s.replace('&#xE1;', 'a')
	s = s.replace('&#xE8;', 'e')
	s = s.replace('%2E', '.')
	s = s.replace('"', ' ')
	s = s.replace('*', ' ')
	s = s.replace('/', ' ')
	s = s.replace(':', ' ')
	s = s.replace('<', ' ')
	s = s.replace('>', ' ')
	s = s.replace('?', ' ')
	s = s.replace('\\', ' ')
	s = s.replace('|', ' ')
	s = s.replace('.', ' ')
	s = s.replace('!', ' ')
	s = s.strip()
	return s

def CreateDirectory(dir_path):
	dir_path = dir_path.strip()
	if not os.path.exists(dir_path):
		os.makedirs(dir_path)
	return

def Notification(title, message):
	xbmc.executebuiltin("XBMC.Notification("+title+","+message+")")
        print message.encode("utf-8")
        return



def guess_series(title):
        """Returns a valid series parser if this :title: appears to be a series"""
        print 'title=' + title
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
                    Notification('ParseWarning:' , pw.value)
                if parser.valid:
                    return parser

def playFile(play_url):
	try:
		#Notification("Streaming", "Streaming")
		listitem = xbmcgui.ListItem('Ironman')
		xbmc.Player().play(urllib.unquote(play_url), listitem)
	except:
		print 'file streaming failed'
		Notification("Streaming failed", "Streaming failed")
        return

def collect(dirs):
                myHistory = getHistory()
                hist = set(myHistory)
                total = len(dirs)
		i = 0.0
		pDialog = xbmcgui.DialogProgress()
                ret = pDialog.create('XBMC', 'Initializing script...')
                        
		for d in dirs:
                        i += 1
                        percent = int( (i * 100) / total)
                        pDialog.update(percent, 'Getting files',str(int(i))+'/'+str(total))
                        #if i % 20 == 1:
                                #Notification(str(total),str(i))
			id = d.getElementsByTagName('id').item(0).firstChild.data
			name = d.getElementsByTagName('name').item(0).firstChild.data
			date = d.getElementsByTagName('date').item(0).firstChild.data
			thumb = d.getElementsByTagName('thumb').item(0).firstChild.data
			if (id + '\n') in hist:
                                continue
			files = getter.getFiles(id)
##			try:
                        addFiles(id,name,files)
                        myHistory.append(id + '\n')
##                        except:
##                                pass
                        if (pDialog.iscanceled()):
                                print 'Canceled scraping'
                                pDialog.close()
                                return
                putHistory(myHistory)
		#Notification("Done","Done")
		#xbmc.UpdateLibrary(video)
		return

def collect2(dirs):
                myHistory = getHistory()
                hist = set(myHistory)
                total = len(dirs)
		i = 0.0
		pDialog = xbmcgui.DialogProgress()
                ret = pDialog.create('XBMC', 'Initializing script...')
                        
		for d in dirs:
                        i += 1
                        percent = int( (i * 100) / total)
                        pDialog.update(percent, 'Getting files',str(int(i))+'/'+str(total))
                        #if i % 20 == 1:
                                #Notification(str(total),str(i))
			id = d.getElementsByTagName('id').item(0).firstChild.data
			name = d.getElementsByTagName('name').item(0).firstChild.data
			date = d.getElementsByTagName('date').item(0).firstChild.data
			thumb = d.getElementsByTagName('thumb').item(0).firstChild.data
			if (id + '\n') in hist:
                                continue
                        else:
                                pass
                                                    
                        targetdir= nameCheck2(name)

                        if targetdir:
                                files = getter.getFiles(id)
                                addFiles2(id,targetdir,files)
                        else:
                                pass
                        myHistory.append(id + '\n')
##                        except:
##                                pass
                        if (pDialog.iscanceled()):
                                print 'Canceled scraping'
                                pDialog.close()
                                return
                putHistory(myHistory)
		#Notification("Done","Done")
		#xbmc.UpdateLibrary(video)
		return




def getHistory():
        try:
                        file = open(HISTORY_FILE, 'r')
                        history = file.readlines()
                        file.close()
                        return history
        except:
                        return list()
                
def putHistory(L):
                file = open(HISTORY_FILE,'w')
                file.writelines(L)
		file.close()
               
def RemoveDirectory(dir):
	dialog = xbmcgui.Dialog()
	if dialog.yesno("Remove directory", "Do you want to remove directory?", dir):
		if os.path.exists(dir):
			pDialog = xbmcgui.DialogProgress()
			pDialog.create(' Removing directory...')
			pDialog.update(0, dir)	
			shutil.rmtree(dir)
			pDialog.close()
			Notification("Directory removed", dir)
		else:
			Notification("Directory not found", "Can't delete what does not exist.")	

def printFiles(files,did):
        xbmcplugin.setContent(int(sys.argv[1]), 'videos')
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
        if not files:
                return
        total = len(files)
        for f in files:
                try:
                        id = f.getElementsByTagName('id').item(0).firstChild.data
                        name = f.getElementsByTagName('name').item(0).firstChild.data
                        play_url = f.getElementsByTagName('url').item(0).firstChild.data
                        url = sys.argv[0] + '?action=playMenow&did=' + did + '&fid=' + id
                        #Notification(name,name)
                        listitem = xbmcgui.ListItem()
                        listitem.setLabel(name)
                        listitem.setInfo('video', {'title': name})
                        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, isFolder=False, totalItems=total)
                        #xbmc.log('f=%s' % name)        
                except:
                        Notification("error","error")
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

def getMovieLens(url):

        req = urllib2.Request(url)
        req.add_header('User-Agent', "%s %s" % (sys.modules[ "__main__" ].__plugin__, sys.modules[ "__main__" ].__version__))
        response = urllib2.urlopen(req)
        soup = BeautifulSoup(response)
        mySpans= soup.findAll('span',attrs={"class" : "movieTitle"})
	##mySpans = mySpans[1], mySpans[2]
        mydirs = list()
	pDialog = xbmcgui.DialogProgress()
	ret = pDialog.create('XBMC', 'Initializing script...')
	i = 0.0
	total = len(mySpans)


        for span in mySpans:
            i += 1
            percent = int( (i * 100) / total)
            pDialog.update(percent, 'Searching ' + span.a.string,str(int(i))+'/'+str(total))


            s = span.a.string
            year = s[len(s)-7 : len(s)]
            year = year.replace('(','').replace(')','')
	    year = year.strip()
            s = s.split('(',1)[0].strip()
            s = s.replace(', The','')
				
            #print s
	    xbmc.log('s=%s' % s)
            dirs= getter.searchDirs(s + ' ' + year)
            if dirs:
                for d in dirs:
                            id = d.getElementsByTagName('id').item(0).firstChild.data
                            name = d.getElementsByTagName('name').item(0).firstChild.data
                            date = d.getElementsByTagName('date').item(0).firstChild.data
                            thumb = d.getElementsByTagName('thumb').item(0).firstChild.data
                            url = sys.argv[0] + '?action=files&did=' + id
			    clean = CleanFileName(name,False)
		            clean = clean.replace('(', '')
                            clean = clean.replace('[', '')
                            clean = clean.replace(']', '')
			    clean = clean.replace(')', '')

                            if s.lower() in clean.lower() and year in name:
			   	##xbmc.log('name=%s' % name)
				mydirs.append(d)
	    if (pDialog.iscanceled()):
		print 'Canceled search'
	        pDialog.close()
                return


        pDialog.close() 
        return mydirs  
