from utils import common
from sites import traktlib
import datetime,sys,time
import xbmcgui,xbmc
import sys
from utils import settings

def addToXbmcLib(fg = None):
	totalAdded=0
	if fg == 'True':
		common.Notification('Getting:','Trending')	
	movies = traktlib.getTrendingMoviesFromTrakt()
	if movies:
		for movie in movies:
			if not movie['watched'] and movie['watchers']>1:
				totalAdded = totalAdded + common.createMovieStrm(movie['title'],movie['year'],movie['imdb_id'])
			        common.createMovieNfo(movie['title'],movie['year'],movie['imdb_id'])

	if fg == 'True':
		common.Notification('Getting:','Recommended')	
	movies = traktlib.getRecommendedMoviesFromTrakt()
	if movies:
	    for movie in movies:
		totalAdded = totalAdded + common.createMovieStrm(movie['title'],movie['year'],movie['imdb_id'])
	        common.createMovieNfo(movie['title'],movie['year'],movie['imdb_id'])
	if fg == 'True':
		common.Notification('Getting:','Watchlist Movies')	
	movies = traktlib.getWatchlistMoviesFromTrakt()
	for movie in movies:
		totalAdded = totalAdded + common.createMovieStrm(movie['title'],movie['year'],movie['imdb_id'])
	        common.createMovieNfo(movie['title'],movie['year'],movie['imdb_id'])


	if fg == 'True':
		common.Notification('Getting:','Calendar Shows')	
	d = datetime.date.today() + datetime.timedelta(days=-8)
	currentdate = d.strftime('%Y%m%d')
	series = traktlib.getShowsCalendarFromTrakt(currentdate)
	for show in series:
	    episodes = show['episodes']
    
	    for episode in episodes:
		myepisode = episode['episode']
	        myshow = episode['show']
		totalAdded = totalAdded + common.createShowStrm(myshow['title'],myepisode['season'],myepisode['number'],myshow['tvdb_id'])
	
#	premieres= getPremieresCalendarFromTrakt(currentdate)
#	for show in premieres:
#	    episodes = show['episodes']
#	    for episode in episodes:
#		myepisode = episode['episode']
#	        myshow = episode['show']
#		season = myepisode['season']
#		if season==1:
#			totalAdded = totalAdded + common.createShowStrm(myshow,myepisode,myshow['tvdb_id'])

	if fg == 'True':		
		common.Notification('Getting:','Watchlist Shows')	
	totalAdded = totalAdded + getWatchlistShows()
	if fg == 'True':
		common.Notification('Total:', str(totalAdded))
	return totalAdded



def getWatchlistShows():
	tot = 0
	shows = traktlib.getWatchlistShowsfromTrakt()
#	for myshow in shows:
#		
#		seasons = traktlib.getSeasons(myshow['tvdb_id'])
#		common.Notification('Getting:', myshow['title'])
#		for season in seasons:
#			if season['season']==0:
#			    continue
#			#print 'Season:' + str(season['season'])
#			episodes = traktlib.getEpisodes(myshow['tvdb_id'],season['season'])
#			for myepisode in episodes:
#				if not False: #myepisode['watched']:
#				#print episode['title']
#					tot = tot + common.createShowStrm(myshow['title'],myepisode['season'],myepisode['number'],myshow['tvdb_id'])
#	return tot

	for myshow in shows:
		if common.checkEnded(myshow['title']) == False:
			fullshow = traktlib.getFullShow(myshow['tvdb_id'])
			seasons = fullshow['seasons']
			common.Notification('Getting:', myshow['title'])
			for season in seasons:
				if season['season']==0:
				    continue
				episodes = season['episodes']
				for myepisode in episodes:
					tot = tot + common.createShowStrm(myshow['title'],myepisode['season'],myepisode['number'],myshow['tvdb_id'])
			common.putShowStatus(fullshow['title'],fullshow['status'])
	return tot


def displayGenres(type):	
	if type == 'Movie':
		genres = traktlib.getMovieGenres()
		url = sys.argv[0]+'?action=trakt_RecommendedMovies&genre=' 
	elif type == 'Show' :
		genres = traktlib.getShowGenres()
		url = sys.argv[0]+'?action=trakt_RecommendedShows&genre=' 

	for genre in genres:
		common.createListItem(genre['name'], True, url+genre['slug'])
	common.endofDir()

def displayRecommendedShows(genre):
	shows = traktlib.getRecommendedShowsFromTrakt(genre)
	for show in shows:
		common.createShowListItemTrakt(show)
	common.endofDir()

def displayProgress():
	progress = traktlib.getProgress()
	for current in progress:
		lastseason = 100
		lastepisode = 100
		for season in current['seasons']:
			seasonnumber = int(season['season'])
			for episode in season ['episodes']:
				if not season ['episodes'][episode]:
					myseason,myepisode = seasonnumber,int(episode)
					if myseason<lastseason:
						lastseason = myseason
						lastepisode = 100
					if myseason==lastseason and myepisode<lastepisode:
						lastepisode = myepisode
					#print '{0} S{1} E{2} / S{3} E{4}'.format(current['show']['title'],myseason,myepisode,lastseason,lastepisode)

		#print '{0} S{1} E{2}'.format(current['show']['title'],lastseason,lastepisode)
		#break
		if lastseason <>100:
			common.createShowListItemTrakt(current['show'],len(progress),lastseason,lastepisode)
	common.endofDir()


def calculateProgress():
	progress = traktlib.getProgress()
	shows = {}
	

	progressByShow = {}
	for current in progress:
		lastseason = 100
		lastepisode = 100
		for season in current['seasons']:
			seasonnumber = int(season['season'])
			for episode in season ['episodes']:
				if not season ['episodes'][episode]:
					myseason,myepisode = seasonnumber,int(episode)
					if myseason<lastseason:
						lastseason = myseason
						lastepisode = 100
					if myseason==lastseason and myepisode<lastepisode:
						lastepisode = myepisode
					#print '{0} S{1} E{2} / S{3} E{4}'.format(current['show']['title'],myseason,myepisode,lastseason,lastepisode)

		#print '{0} S{1} E{2}'.format(current['show']['title'],lastseason,lastepisode)
		#break
		show = {}
		if lastseason<>100:
			shows[current['show']['title']]= (lastseason,lastepisode)
	return shows


def displayRecommendedMovies(genre):
	movies = traktlib.getRecommendedMoviesFromTrakt(genre)
	for movie in movies:
		common.createMovieListItemTrakt(movie,totalItems = len(movies))
	common.endofDir()
	return

def traktSeenRate(imdbid):
	mymovie = traktlib.getMovieInfobyImdbid(imdbid)
	movie = {}
	movie['imdb_id'] = mymovie['imdb_id']
	movie['title']= mymovie['title']
	movie['year']= mymovie['year']
	ratings = []
	for i in range(1,11):
		ratings.append(str(i))
	dialog = xbmcgui.Dialog()
	myrating = dialog.select('Rating', ratings)
	if myrating==-1: return
	movie['rating'] = ratings[myrating]
	response = traktlib.setRating(movie,'movie')
	common.traktResponse(response)
	args = {}
	movie = {}
	args['movies'] = []
	movie['imdb_id'] = mymovie['imdb_id']
	movie['title']= mymovie['title']
	movie['year']= mymovie['year']
	movie['plays'] = 1
	movie['last_played'] = int(time.time())
	args['movies'].append(movie)
	traktlib.setSeen(args)
	return

def traktSeenShow(tvdbid,season,episode):
	show = {}
	show['tvdb_id'] = tvdbid
	if season==100:
		ratings = []
		for i in range(1,11):
			ratings.append(str(i))
		dialog = xbmcgui.Dialog()
		myrating = dialog.select('Rating', ratings)
		if myrating==-1: return
		show['rating'] = ratings[myrating]
		response = traktlib.setRating(show,'show')
		common.traktResponse(response)
	
	response = traktlib.setShowSeen(tvdbid,season,episode)
	common.traktResponse(response)


	return

def traktDismissMovie(imdbid):
	response = traktlib.dismissMovie(imdbid)
	common.Notification(response['status'],response['message'])

def addShowtoWatchlist(tvdbid):
	response = traktlib.addShowtoWatchList(tvdbid)
	common.traktResponse(response)
	getWatchlistShows()
	xbmc.executebuiltin('UpdateLibrary(video)')

def traktDismissShow(tvdbid):
	response = traktlib.dismissShow(tvdbid)
	common.Notification(response['status'],response['message'])

def addMovietoWatchlist(imdbid):
	response = traktlib.addMovietoWatchlist(imdbid)
	common.traktResponse(response)
	movies = traktlib.getWatchlistMoviesFromTrakt()
	for movie in movies:
		common.createMovieStrm(movie['title'],movie['year'],movie['imdb_id'])
	        common.createMovieNfo(movie['title'],movie['year'],movie['imdb_id'])
	xbmc.executebuiltin('UpdateLibrary(video)')



def traktAction(params):
	if(params['action'] == 'trakt_Menu'):
		displayTraktMenu()
	
	elif(params['action'] == 'trakt_SearchMovies'):
	        # Search
	        keyboard = xbmc.Keyboard('', 'Search')
		keyboard.doModal()
	        if keyboard.isConfirmed():
		        query = keyboard.getText()
			movies = traktlib.getMovieInfobySearch(unicode(query))
			for movie in movies:
				common.createMovieListItemTrakt(movie,totalItems = len(movies))
			common.endofDir()
	
	elif(params['action'] == 'trakt_SearchShows'):
	        # Search
	        keyboard = xbmc.Keyboard('', 'Search')
		keyboard.doModal()
	        if keyboard.isConfirmed():
		        query = keyboard.getText()
			shows = traktlib.getShowInfobySearch(unicode(query))
			for show in shows:
				common.createShowListItemTrakt(show,totalItems = len(shows))
			common.endofDir()
	
		
	elif(params['action'] == 'trakt_SeenRate'):
		imdbid = params['imdbid']
		traktSeenRate(imdbid)

	elif(params['action'] == 'trakt_DismissMovie'):
		imdbid = params['imdbid']
		traktDismissMovie(imdbid)

	elif(params['action'] == 'trakt_MovieGenres'):
		displayGenres(type='Movie')

	elif(params['action'] == 'trakt_ShowGenres'):
		displayGenres(type='Show')


	elif(params['action'] == 'trakt_RecommendedShows'):
		try:
			genre = params['genre']
		except:
			genre = None
		if genre:
			displayRecommendedShows(genre)
		else :			
			url = sys.argv[0]+'?action=trakt_ShowGenres' 
			common.createListItem('Filter by Genre', True, url)
			displayRecommendedShows(genre)

		

	elif(params['action'] == 'trakt_RecommendedMovies'):
		try:
			genre = params['genre']
		except:
			genre = None
		if genre:
			displayRecommendedMovies(genre)
		else :			
			url = sys.argv[0]+'?action=trakt_MovieGenres' 
			common.createListItem('Filter by Genre', True, url)
			displayRecommendedMovies(genre)


	elif(params['action'] == 'trakt_AddShowtoWatchlist'):
		tvdbid = params['tvdbid']
		addShowtoWatchlist(tvdbid)
	
	elif(params['action'] == 'trakt_AddMovietoWatchlist'):
		imdbid = params['imdbid']
		addMovietoWatchlist(imdbid)

	elif(params['action'] == 'trakt_RemoveMoviefromWatchlist'):
		imdbid = params['imdbid']
		response = traktlib.removeMoviefromWatchlist(imdbid)
		common.traktResponse(response)

	elif(params['action'] == 'trakt_DismissShow'):
		tvdbid = params['tvdbid']
		traktDismissShow(tvdbid)
	
	elif(params['action'] == 'trakt_SetShowSeen'):
		tvdbid = params['tvdbid']
		try:
			season = params['season']
			episode = params['episode']
		except:
			season = 100
			episode = 100
		response = traktSeenShow(tvdbid,season,episode)

	elif(params['action'] == 'trakt_TrendingMovies'):
		movies = traktlib.getTrendingMoviesFromTrakt()
		for movie in movies:
			common.createMovieListItemTrakt(movie,totalItems = len(movies))
		common.endofDir()

	elif(params['action'] == 'trakt_TrendingShows'):
		shows = traktlib.getTrendingShowsFromTrakt()
		progressShows = calculateProgress()
		for show in shows:
			if show['title'] in progressShows:
				common.createShowListItemTrakt(show,len(shows),progressShows[show['title']][0],progressShows[show['title']][1])
			else:
				common.createShowListItemTrakt(show,totalItems = len(shows))
		common.endofDir()
	
	elif(params['action'] == 'trakt_Progress'):
		displayProgress()
	else:
		common.Notification('Action Not found:' , params['action'])

def displayTraktMenu():
	
	url = sys.argv[0]+'?action=' 
	common.createListItem('Recommended Movies', True, url+'trakt_RecommendedMovies')
	common.createListItem('Trending Movies', True, url +'trakt_TrendingMovies')
	common.createListItem('Search Movies', True, url +'trakt_SearchMovies')
	common.createListItem('--------------------------------------------', False, '')
	common.createListItem('Tv Show Progress', True, url+'trakt_Progress')
	common.createListItem('Recommended Shows', True, url +'trakt_RecommendedShows')
	common.createListItem('Trending Shows', True, url +'trakt_TrendingShows')
	common.createListItem('Search Shows', True, url +'trakt_SearchShows')

	common.endofDir()
