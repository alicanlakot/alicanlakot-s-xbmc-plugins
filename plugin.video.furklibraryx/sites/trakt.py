from utils import common,settings
from sites import traktlib, furklib
import datetime,sys,time
import xbmcgui,xbmc
import sys
from utils import settings

def addToXbmcLib(fg = None):
    totalAdded=0
    if settings.getSetting("auto_addImdb"):
        imdbmovies = imdb.watchlist_movies(url,0)
        traktlib.addMoviestoWatchlist(imdbmovies)
        imdbshows = imdb.watchlist_shows(url,0)
        traktlib.addShowstoWatchlist(imdbshows)


	if settings.getSetting("add_trending"):
	    	if fg == 'True':
    			common.Notification('Getting:','Trending')
	    	movies = traktlib.getTrendingMoviesFromTrakt()
    		if movies:
    			for movie in movies:
    				if not movie['watched'] and movie['watchers']>1:
    					totalAdded = totalAdded + common.createMovieStrm(movie['title'],movie['year'],movie['imdb_id'])
    					common.createMovieNfo(movie['title'],movie['year'],movie['imdb_id'])


	if settings.getSetting("add_recommended"):
		if fg == 'True':
			common.Notification('Getting:','Recommended')
		movies = traktlib.getRecommendedMoviesFromTrakt()
		if movies:
		    for movie in movies:
			totalAdded = totalAdded + common.createMovieStrm(movie['title'],movie['year'],movie['imdb_id'])
			common.createMovieNfo(movie['title'],movie['year'],movie['imdb_id'])

	if settings.getSetting("add_watchlistmovies"):
		if fg == 'True':
			common.Notification('Getting:','Watchlist Movies')
		movies = traktlib.getWatchlistMoviesFromTrakt()
		for movie in movies:
			totalAdded = totalAdded + common.createMovieStrm(movie['title'],movie['year'],movie['imdb_id'])
			common.createMovieNfo(movie['title'],movie['year'],movie['imdb_id'])

	if settings.getSetting("add_watchlistshows"):
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
    shows = calculateProgress()

    for show in shows:
        if show['season'] <>0:
            common.createShowListItemTrakt(show,len(shows),show['season'],show['episode'])
    common.endofDir()


def calculateProgress():
    progress = traktlib.getProgress()
    shows = []
    for current in progress:
        showprogress = {}
        if current['next_episode'] <> False :
            lastseason = current['next_episode']['season']
            lastepisode = current['next_episode']['num']
        else:
            lastseason = 0
            lastepisode= 0
        showprogress['title'] = current['show']['title']
        showprogress['season'] = lastseason
        showprogress['episode'] = lastepisode
        showprogress['tvdb_id'] = current['show']['tvdb_id']
        shows.append(showprogress)
    return shows

def displayList(user,slug):
	myList = traktlib.getList(user,slug)
	movies = []
	for item in myList['items']:
		if item['type']=="movie":
			myMovie = item['movie']
			myMovie['watched']=item['watched']
			movies.append(myMovie)
	for movie in movies:
		print movie['watched']
		common.createMovieListItemTrakt(movie,totalItems = len(movies))
	common.endofDir()
	return

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

	elif(params['action'] == 'trakt_listfeeds'):
			myfeeds = furklib.myFeeds()['feeds']
			myfeeds = sorted(myfeeds,key=lambda feed: feed['name'])
			url = sys.argv[0]+'?action=trakt_addfeeds'
			common.createListItem('Add Feeds from trakt', True, url)
			for feed in myfeeds:
				url = sys.argv[0]+'?action=trakt_MovieGenres'
				common.createListItem(feed['name'], True, url)
			common.endofDir()

	elif(params['action'] == 'trakt_addfeeds'):
			myfeeds = furklib.myFeeds()['feeds']
			shows = traktlib.getWatchlistShowsfromTrakt()
			progress = traktlib.getProgress()
			series = []
			for current in progress:
				series.append(current['show'])
			shows = shows + series
			for show in shows:
				check = [feed for feed in myfeeds if feed['name'] == show['title']]
				if len(check)==0:
					furklib.addFeed(show['title'])
					url = sys.argv[0]+'?action=trakt_MovieGenres'
					common.createListItem(show['title'], False, '')
			common.endofDir()



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
	elif(params['action'] == 'trakt_getList'):
		user=params['user']
		slug=params['slug']
		displayList(user,slug)
	else:
		common.Notification('Action Not found:' , params['action'])

def displayTraktMenu():

	url = sys.argv[0]+'?action='
	common.createListItem('--------------FEEDS------------------', False, '')
	common.createListItem('List my feeds', True, url+'trakt_listfeeds')
	common.createListItem('--------------MOVIES------------------', False, '')
	common.createListItem('Recommended Movies', True, url+'trakt_RecommendedMovies')
	common.createListItem('Trending Movies', True, url +'trakt_TrendingMovies')
	common.createListItem('Search Movies', True, url +'trakt_SearchMovies')
	common.createListItem('--------------SHOWS-----------------------', False, '')
	common.createListItem('Tv Show Progress', True, url+'trakt_Progress')
	common.createListItem('Recommended Shows', True, url +'trakt_RecommendedShows')
	common.createListItem('Trending Shows', True, url +'trakt_TrendingShows')
	common.createListItem('Search Shows', True, url +'trakt_SearchShows')
	common.createListItem('---------------LISTS----------------------', False, '')
	common.createListItem('Academy Award For Best Picture by chrisu', True, url +'trakt_getList&user=chrisu&slug=academy-award-for-best-picture')
	common.createListItem('James Bond 007 Collection by ltfearme', True, url +'trakt_getList&user=ltfearme&slug=james-bond-007-collection')
	#http://trakt.tv/user/ltfearme/lists/james-bond-007-collection
	common.createListItem('ALL IMDB Top 250 Movies Ever by totopsgr', True, url +'trakt_getList&user=totopsgr&slug=all-imdb-top-250-movies-ever')
	#http://trakt.tv/user/totopsgr/lists/all-imdb-top-250-movies-ever
	common.createListItem('Best Mindfucks by BenFranklin', True, url +'trakt_getList&user=BenFranklin&slug=best-mindfucks')
	#http://trakt.tv/user/BenFranklin/lists/best-mindfucks
	common.createListItem('Studio Ghibli Feature-films by Draackje', True, url +'trakt_getList&user=Draackje&slug=studio-ghibli-feature-films')
	#http://trakt.tv/user/Draackje/lists/studio-ghibli-feature-films
	common.createListItem('Criterion Collection by gubarenko', True, url +'trakt_getList&user=gubarenko&slug=criterion-collection')
	#http://trakt.tv/user/gubarenko/lists/criterion-collection
	common.endofDir()
