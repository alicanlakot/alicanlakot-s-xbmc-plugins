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
import datetime
import md5

from ext.titles.series import SeriesParser
from ext.titles.movie import MovieParser
from ext.titles.parser import TitleParser, ParseWarning
from ext import feedparser
from ext.BeautifulSoup import BeautifulSoup
from sites import traktlib
from sites import furklib


#import feedparser

__settings__ = sys.modules[ "__main__" ].__settings__
ADDON = xbmcaddon.Addon(id='plugin.video.furklibrary')
##MOVIES_PATH= os.path.join('C:/Users/altasak/XBMC/movies','')
##TV_SHOWS_PATH = os.path.join('C:/Users/altasak/XBMC/shows2','')
furk_username= ADDON.getSetting('login')
furk_password= ADDON.getSetting('password')
#furk_apikey = furklib.login(furk_username,furk_password)
furk_apikey = '1219bc29fdc017785ec7ba296ed58e579b29f48f'
if ADDON.getSetting('movie_custom_directory') == "true":
	MOVIES_PATH = ADDON.getSetting('movie_directory')
else:
	MOVIES_PATH = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.furklibrary/movies'), '')

if ADDON.getSetting('tv_show_custom_directory') == "true":
	TV_SHOWS_PATH = ADDON.getSetting('tv_show_directory')
else:
	TV_SHOWS_PATH = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.furklibrary/tvshows'), '')

OTHERS_PATH = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.furklibrary/others'), '')
VCDQ_PATH = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.furklibrary/vcdq'), '')
HISTORY_FILE = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.furklibrary'), 'history.txt')
# Trakt
apikey = '7a933ed6ba1c34da229231dd0e9dfc63'
username= 'akina'
pwd = 'altasa'
headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
# End Trakt
		
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
                                                print 'name =' + name.encode("utf-8")
                                                print 'myquality=' + myquality.name
                                                mydir= os.path.join(MOVIES_PATH , myquality.name ,movie_name)
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
		if not os.path.isfile(path):
			file = open(path,'w')
			file.write(strm_string)
			file.close()
	except:
		pass
		Notification("Error while creating strm file for : " , name)
        

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
                        #url = sys.argv[0] + '?action=playMenow&did=' + did + '&fid=' + id
			url = play_url
                        #Notification(name,name)
                        listitem = xbmcgui.ListItem()
                        listitem.setLabel(name)
                        listitem.setInfo('video', {'title': name})
                        xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem, isFolder=False, totalItems=total)
                        #xbmc.log('f=%s' % name)        
                except:
                        Notification("error","error")
        xbmcplugin.endOfDirectory(int(sys.argv[1]))



def getVCDQ(url):

	d = feedparser.parse( url )
	Notification("Navigating to ",d['feed']['title'])
	


	##mySpans = mySpans[1], mySpans[2]
        mydirs = list()
	pDialog = xbmcgui.DialogProgress()
	ret = pDialog.create('XBMC', 'Initializing script...')
	i = 0.0
	total = len(d.entries)


        for span in d.entries:
            i += 1
            percent = int( (i * 100) / total)
            pDialog.update(percent, 'Searching ' + span.title,str(int(i))+'/'+str(total))
	    ##if (i>5):
		##break


            rssname = span.title
            parser = MovieParser()
	    parser.data = rssname
            parser.parse()
            myName = parser.name 
            myYear = parser.year

            #year = s[len(s)-7 : len(s)]
            #year = year.replace('(','').replace(')','')
	    #year = year.strip()
            #s = s.split('(',1)[0].strip()
            #s = s.replace(', The','')
				
            #print s
	    s = myName + '(' + str(myYear) + ')'
	    xbmc.log('s=%s' % s)
            dirs= getter.searchDirs(s)
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
                            if '720p' in clean.lower():
  				    mydirs.append(d)

	    if (pDialog.iscanceled()):
		print 'Canceled search'
	        pDialog.close()
                return


        pDialog.close() 
        return mydirs  


def getMovieLenstoLib(url):

        req = urllib2.Request(url)
        req.add_header('User-Agent', "%s %s" % (sys.modules[ "__main__" ].__plugin__, sys.modules[ "__main__" ].__version__))
        response = urllib2.urlopen(req)
        soup = BeautifulSoup(response)
        mySpans= soup.findAll('span',attrs={"class" : "movieTitle"})
	##mySpans = mySpans[1], mySpans[2]

	pDialog = xbmcgui.DialogProgress()
	ret = pDialog.create('XBMC', 'Initializing script...')
	i = 0.0
	total = len(mySpans)


        for span in mySpans:
	    time.sleep(2)
            i += 1
            percent = int( (i * 100) / total)
            pDialog.update(percent, 'Searching ' + span.a.string,str(int(i))+'/'+str(total))
	    s = span.a.string
            year = s[len(s)-7 : len(s)]
            year = year.replace('(','').replace(')','')
	    year = year.strip()
            s = s.split('(',1)[0].strip()
            s = s.replace(', The','')
	    s = s + ' (' + year + ')' 
            #print s
            i += 1
            percent = int( (i * 100) / total)
            pDialog.update(percent, 'Searching ' + s,str(int(i))+'/'+str(total))

            rssname = s.encode('ascii', 'ignore')
            parser = MovieParser()
	    parser.data = rssname
            parser.parse()
            myName = parser.name 
            myYear = parser.year

	    s = myName + ' (' + str(myYear) + ')'
	    xbmc.log('s=%s' % repr(s))

	    if myYear:
                url = 'plugin://plugin.video.furklibrary/' + '?action=SearchMe&q=' + s	
		strmfilename = CleanFileName(s,False)
		CreateStreamFile(strmfilename,url,VCDQ_PATH,False)

	    if (pDialog.iscanceled()):
		print 'Canceled search'
	        pDialog.close()
                return


        pDialog.close() 
        return


def getVCDQtoLibrary(url):

	d = feedparser.parse( url )
	Notification("Navigating to ",d['feed']['title'])
	xbmc.log (d['feed']['title'])
	mydirs = list()
	pDialog = xbmcgui.DialogProgress()
	ret = pDialog.create('XBMC', 'Initializing script...')
	i = 0.0
	total = len(d.entries)


        for span in d.entries:
            i += 1
            percent = int( (i * 100) / total)
            pDialog.update(percent, 'Searching ' + span.title,str(int(i))+'/'+str(total))
	    ##if (i>5):
		##break


            rssname = span.title
            parser = MovieParser()
	    parser.data = rssname
            parser.parse()
            myName = parser.name 
            myYear = parser.year

	    s = myName + ' (' + str(myYear) + ')'
	    xbmc.log('s=%s' % s)

	    if myYear:
		searchquery = CleanFileName(s, False)
                url = 'plugin://plugin.video.furklibrary/' + '?action=SearchMe&q=' + searchquery
		strmfilename = CleanFileName(s,False)
		CreateStreamFile(strmfilename,url,VCDQ_PATH,False)

	    if (pDialog.iscanceled()):
		print 'Canceled search'
	        pDialog.close()
                return


        pDialog.close() 
        return 



