import sys, urllib, time, re, os
import xbmc, xbmcaddon, xbmcgui, xbmcplugin
from utils import common
from utils import searcher

def parse_qs(u):
	params = '?' in u and dict(p.split('=') for p in u[u.index('?') + 1:].split('&')) or {}
	
	return params;

def AddonMenu():  #homescreen
	print 'FurkLibrary menu'
	url = sys.argv[0]+'?action=music_' 
	#common.createListItem(params['content_type'],True,url + 'myFiles')
	common.createListItem('Search',True,url + 'search')
	common.createListItem('My Files',True,url + 'myFiles')
	common.createListItem('Setup',False,url +'setup')
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


def musicAction(params):

	if(params['action'] == 'about'):
		# Play a file
		collector.Notification(__plugin__,__version__)

	elif(params['action'] == 'music_search'):
		# Search
		keyboard = xbmc.Keyboard('', 'Search')
		keyboard.doModal()

		if keyboard.isConfirmed():
			query = keyboard.getText()
			searcher.SearchFromMenu(query)

	elif(params['action'] == 'music_myFiles'):
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
		xbmc.executebuiltin('UpdateLibrary(video)')

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
			title = params['title']
			year = params['year']
			imdbid = params['imdbid']
			movie = common.getMovieInfobyImdbid(imdbid)
		else:
			type = 'Movie'
			title = params['query']

		try:
			go = params['go']
			go = True
		except:
			go = False

		


		myname,myurl = searcher.SearchDialog(type,title,year,season,episode)
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


	elif(params['action'] == 'traktlib'):
		try:
			fg = params['fg']
		except:
			fg = 'True'
		totalAdded = trakt.addToXbmcLib(fg)
		totalAdded += imdb.addImdbToLib(fg)

		if totalAdded>0:
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
			music.MusicMenu()
			

	print 'Closing FurkLib'
	#sys.modules.clear()




