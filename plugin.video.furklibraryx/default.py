'''
    Furk.net player / scraper for XBMC
    Copyright (C) 2011 Alican Lakot

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

import sys, urllib, time, re, os
import xbmc, xbmcaddon, xbmcgui, xbmcplugin
import context
from utils import settings

# Plugin constants
__plugin__ = 'Furk.net Library X'
__author__ = 'Alican Lakot'
__url__ = 'http://www.furk.net/?INVITE=1216084'
__version__ = '1.2.0'

FIRST_TIME_STARTUP = settings.first_time_startup()

print "[PLUGIN] '%s: version %s' initialized!" % (__plugin__, __version__)

if settings.getSetting('tv_show_custom_directory') == "true":
	TV_SHOWS_PATH = settings.getSetting('tv_show_directory')
else:
	TV_SHOWS_PATH = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.furklibraryx/tvshows'), '')

if settings.getSetting('movie_custom_directory') == "true":
	MOVIES_PATH = settings.getSetting('movie_directory')
else:
	MOVIES_PATH = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.furklibraryx/movies'), '')

CACHE_PATH= os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.furklibraryx/traktcache'), '')
try:
	MYCONTEXT = context.context().getContext()
except:
	MYCONTEXT = 'video'

IMDB_WATCHLIST = "http://akas.imdb.com/user/" + settings.getSetting("imdb_watchlist") + "/watchlist?"

from utils import searcher
from utils import common
from sites import trakt,traktlib
from sites import movielens
from sites import criticker
from sites import vcdq
from sites import imdb
from sites import torrentfreak
from sites import furklib
from sites import rotten
import music

print sys.modules[ "__main__" ]

def parse_qs(u):
	params = '?' in u and dict(p.split('=') for p in u[u.index('?') + 1:].split('&')) or {}

	return params;

def AddonMenu():  #homescreen
	print 'FurkLibrary menu'
	url = sys.argv[0]+'?action='
	#common.createListItem(params['content_type'],True,url + 'myFiles')

	common.createListItem('My Files',True,url + 'myFiles')
	common.createListItem('Search',True,url + 'search')
	common.createListItem('Trakt',True,url + 'trakt_Menu')
	common.createListItem('Trailers',False,url + 'Trailers')
	common.createListItem('Rotten Tomatoes',True,url + 'rotten_Menu')
	common.createListItem('Add watchlist to your library',False,url + 'traktlib')
	common.createListItem('VCDQ New Releases',True, url + 'vcdq')
	#common.createListItem('MovieLens',True, url + 'movielens')
	common.createListItem('IMDB',True, url + 'imdb_Menu&page=1')
	common.createListItem('Torrentfreak Top 10',True, url + 'torrentfreak')
	common.createListItem('Criticker (Beta)',True, url + 'criticker')
	common.createListItem('Setup',False,url +'setup')
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


def setup_sources():
    xbmc.log("Trying to add source paths...")
    source_path = os.path.join(xbmc.translatePath('special://profile/'), 'sources.xml')

    try:
        f = open(source_path, 'a+')
	f.seek(0)
        content = f.read()
        f.close()
        r = re.search("(?i)(<sources>[\S\s]+?<video>[\S\s]+?>)\s+?(</video>[\S\s]+?</sources>)", content)
	if r:
	        new_content = r.group(1)
	else:
		new_content = '<sources><video>'
        if not check_sources_xml(MOVIES_PATH):
            new_content += '<source><name>Movies (furklib2)</name><path pathversion="1">'
            new_content += MOVIES_PATH
            new_content += '</path></source>'
        if not check_sources_xml(TV_SHOWS_PATH):
            new_content += '<source><name>TV Shows (furklib2)</name><path pathversion="1">'
            new_content += TV_SHOWS_PATH
            new_content += '</path></source>'
	if r:
	        new_content += r.group(2)
	else:
	        new_content += '</video></sources>'

        f = open(source_path, 'w')
        f.write(new_content)
        f.close()

        dialog = xbmcgui.Dialog()
        dialog.ok("Source folders added", "To complete the setup:", " 1) Restart XBMC.", " 2) Set the content type of added sources.")
        #if dialog.yesno("Restart now?", "Do you want to restart XBMC now?"):
		#xbmc.restart()
    except:
	raise
        xbmc.log("Could not edit sources.xml")

def check_sources_xml(path):
    try:
        source_path = os.path.join(xbmc.translatePath('special://profile/'), 'sources.xml')
        f = open(source_path, 'a+')
	f.seek(0)
        content = f.read()
        f.close()
        path = str(path).replace('\\', '\\\\')
        if re.search(path, content):
            return True
    except:
        xbmc.log("Could not find sources.xml!")
    return False

def setup():
    if FIRST_TIME_STARTUP:
        dialog = xbmcgui.Dialog()
        dialog.ok("Furk Library BY alicanlakot","..","Welcome to first time", "setup")
	if not check_sources_xml(MOVIES_PATH) or not check_sources_xml(TV_SHOWS_PATH):
            if dialog.yesno("Setup folder", "The directories used are not listed as video sources.", "Do you want to add them to sources.xml now?"):
                setup_sources()
	data = traktlib.testUser(settings.getSetting('trakt_login'),settings.getSetting('trakt_password'))
	if data['status'] =='failure' :
		common.Notification(data['status'],'Please check your username for Trakt and Furk in config')
		settings.openSettings()
		data = traktlib.testUser(settings.getSetting('trakt_login'),settings.getSetting('trakt_password'))
		common.Notification('Tried again:',data['status'])
	if len(settings.getSetting('furk_apikey')) < 5:
		furklib.login(settings.getSetting('furk_login'),settings.getSetting('furk_password'))

	dialog.ok("Furk Library BY alicanlakot","..","You can start this again", "from menu")
        settings.setSetting('first_time_startup', 'false')

xbmc.log('params_str=%s' % sys.argv[2])
params = parse_qs(sys.argv[2])
if not params:
        params['action'] = 'dirs'
try:
	action = params['action']
except:
	params['action'] = 'dirs'
xbmc.log('_params=%s' % params)


if(params['action'] == 'about'):
        # Play a file
	collector.Notification(__plugin__,__version__)

elif(params['action'] == 'search'):
        # Search
        keyboard = xbmc.Keyboard('', 'Search')
        keyboard.doModal()

        if keyboard.isConfirmed():
                query = keyboard.getText()
                searcher.SearchFromMenu(query)

elif(params['action'] == 'myFiles'):
         searcher.getMyFiles()


elif(params['action'] == 'listFiles'):
	id = params['id']
	searcher.ListFiles(id)

elif(params['action'] == 'movielens'):
        # Search
        movielens.displayMovieLensmenu()

elif(params['action'] == 'movielensUrl'):
        # Search
	url = params['url']
	xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        movielens.getMovieLens(url)
	common.endofDir()

elif(params['action'] == 'criticker'):
        # Search
	xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	criticker.getCriticker()

elif(params['action'] == 'vcdq'):
	url1 = "http://www.vcdq.com/browse/rss/1/0/0/10_9_11_3_2_6_4/0/0/0"
	xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        vcdq.getVCDQ(url1)

elif(params['action'] == 'torrentfreak'):
	xbmcplugin.setContent(int(sys.argv[1]), 'movies')
	url1 = "http://torrentfreak.com/category/dvdrip/feed/"
        torrentfreak.getpopular(url1)


elif(params['action'] == 'scrapeMovie'):
        title = params['title']
	year = params['year']
	common.createMovieStrm(title,year,MOVIES_PATH)
	common.Notification ('Added to library:',title)
	xbmc.executebuiltin('Library(video)')

elif(params['action'] == 'Trailers'):
	#xbmc.executebuiltin("XBMC.RunScript(special://home/addons/script.furktrailers/default.py)")
	xbmc.executebuiltin("XBMC.RunScript(special://home/addons/plugin.video.furklibraryx/trailers.py)")

elif(params['action'] == 'SearchMe'):
        # Search
    type = params['type']
    year= 0
    season = 0
    episode = 0
    movie = None
    if type=='Show':
        type = params['type']
        season = params['season']
        episode = params['episode']
        title = params['title']
        try:
            tvdbid = params['tvdbid']
        except:
		    tvdbid = None
        if tvdbid:
            episodedata = traktlib.getEpisodeInfo(tvdbid,season,episode)
        else:
            episodedata = None

    elif type=='Movie':
        imdbid = params['imdbid']
        movie = common.getMovieInfobyImdbid(imdbid)
        if movie:
			title = movie['title']
			year = movie['year']
        else:
			title = params['title']
			year = params['year']
    else:
		type = 'Movie'
		title = params['query']

    go = False
    try:
        go = params['go']
        if go:
            go=True
    except:
		go = False



    print go
    myname,myurl = searcher.SearchDialog(type,title,year,season,episode,go)



    if myurl:
		#common.Notification("Found"," and playing!")
        time.sleep(1)
        listitem = xbmcgui.ListItem(myname, path=myurl)
        listitem.setLabel(myname)
        listitem.setProperty("IsPlayable", "true")
        if movie:
		          common.addMovieInfotoPlayListitem(listitem,movie)
			#common.Notification("Found"," Movie!")

        elif episodedata:
			common.addEpisodeInfotoListitem(listitem,episodedata)

        xbmcplugin.setResolvedUrl(int(sys.argv[ 1 ]),True,listitem)
        print myname
        print myurl
        if go:
			xbmc.Player().play(myurl, listitem)
        else:
            xbmcplugin.setResolvedUrl(int(sys.argv[ 1 ]),False,xbmcgui.ListItem())

elif(params['action'].startswith('imdb_')):
	imdb.imdbAction(params)

elif(params['action'].startswith('trakt_')):
	trakt.traktAction(params)

elif(params['action'].startswith('rotten_')):
	rotten.rottenAction(params)

elif(params['action'].startswith('music_')):
	music.musicAction(params)


elif(params['action'] == 'traktlib'):
    try:
        fg = params['fg']
    except:
        fg = 'True'
	totalAdded = trakt.addToXbmcLib()
	#totalAdded += imdb.addImdbToLib(fg)

	if totalAdded>=0:
		common.Notification('Furk-Trakt', '{0} were added'.format(totalAdded))
	xbmc.executebuiltin('UpdateLibrary(video)')
	if fg=='False':
		settings.startTimer()


elif(params['action'] == 'download'):
	url = params['url']
	filename = params['filename']
	common.download(url,filename)



elif(params['action'] == 'setup'):
	settings.setSetting('first_time_startup','true')
	FIRST_TIME_STARTUP = settings.first_time_startup()
	setup()

else:
        # torrents a root Directories
        xbmc.log('argv=%s' % sys.argv)
	if (MYCONTEXT == 'video'):
		common.createCachePath()
		setup()
		AddonMenu()
	else:
		music.AddonMenu()


print 'Closing FurkLib'
#sys.modules.clear()




