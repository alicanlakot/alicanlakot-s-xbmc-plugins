import json
import httplib
import os
import unicodedata
from xml.dom.minidom import Document
from utils import settings

# Trakt
apikey = '7a933ed6ba1c34da229231dd0e9dfc63'
headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
# End Trakt


def testUser(username,pwd):
	data = traktJsonRequest('POST', '/account/test/%%API_KEY%%',args = {},returnStatus=True)
	if data == None:
		print("Error in request from 'getTrendingMoviesFromTrakt()'")
	return data



# get a connection to trakt
def getTraktConnection():
    conn = httplib.HTTPConnection('api.trakt.tv')
    return conn
    
# make a JSON api request to trakt
# method: http method (GET or POST)
# req: REST request (ie '/user/library/movies/all.json/%%API_KEY%%/%%USERNAME%%')
# args: arguments to be passed by POST JSON (only applicable to POST requests), default:{}
# returnStatus: when unset or set to false the function returns None apon error and shows a notification,
#   when set to true the function returns the status and errors in ['error'] as given to it and doesn't show the notification,
#   use to customise error notifications
# anon: anonymous (dont send username/password), default:False
# connection: default it to make a new connection but if you want to keep the same one alive pass it here
# silent: default is False, when true it disable any error notifications (but not print messages)
# passVersions: default is False, when true it passes extra version information to trakt to help print problems
def traktJsonRequest(method, req, args={}, returnStatus=False, anon=False, conn=False, silent=False, passVersions=False):
    closeConnection = False
    conn = getTraktConnection()
    closeConnection = True
    req = 'http://api.trakt.tv' + req
    req = req.replace("%%API_KEY%%",apikey)
    req = req.replace("%%USERNAME%%",settings.getSetting('trakt_login'))
    if method == 'POST':
            if not anon:
                args['username'] = settings.getSetting('trakt_login')
                args['password'] = settings.getSetting('trakt_password')
            if passVersions:
                args['plugin_version'] = __settings__.getAddonInfo("version")
                args['media_center'] = 'xbmc'
                args['media_center_version'] = xbmc.getInfoLabel("system.buildversion")
                args['media_center_date'] = xbmc.getInfoLabel("system.builddate")
            jdata = json.dumps(args)
            #print(req)
            #print(jdata)
            conn.request('POST', req, jdata)
    elif method == 'GET':
            args['username'] = settings.getSetting('trakt_login')
            args['password'] = settings.getSetting('trakt_password')
            jdata = json.dumps(args)
            conn.request('GET', req, jdata)
            #print("trakt json url: "+req)
    #conn.go()
    try:
	response = conn.getresponse()
	raw = response.read()
	data = json.loads(raw)

    except:
	return None
    
    if 'status' in data:
        if data['status'] == 'failure':
            print("traktQuery: Error: " + str(data['error']))
            if returnStatus:
                return data
            return None

    return data

# returns list of movies from watchlist
def getWatchlistMoviesFromTrakt():
    data = traktJsonRequest('POST', '/user/watchlist/movies.json/%%API_KEY%%/%%USERNAME%%')
    if data == None:
        print("Error in request from 'getWatchlistMoviesFromTrakt()'")
    return data

def getRecommendedMoviesFromTrakt(genre = None):
    args = {}
    if genre:
	    args['genre'] = genre
	    #print 'genre:' + genre

    data = traktJsonRequest('POST', '/recommendations/movies/%%API_KEY%%',args)
    if data == None:
        print("Error in request from 'getWatchlistMoviesFromTrakt()'")
    return data

def getRecommendedShowsFromTrakt(genre):
    args = {}
    args['hide_watchlisted'] = True
    if genre:
	    args['genre'] = genre
	    
    data = traktJsonRequest('POST', '/recommendations/shows/%%API_KEY%%' ,args)

    if data == None:
	    print("Error in request from 'getWatchlistMoviesFromTrakt()'")
    return data

def dismissShow(tvdbid):
	args = {}
	args['tvdb_id'] = tvdbid
	data = traktJsonRequest('POST', '/recommendations/shows/dismiss/%%API_KEY%%' ,args)
	if data == None:
	    print("Error in request from 'getWatchlistMoviesFromTrakt()'")
	return data


def addShowtoWatchList(tvdbid):
    args = {}
    shows = []
    show = {}
    show['tvdb_id'] = tvdbid
    shows.append(show)
    args['shows'] = shows
    data = traktJsonRequest('POST', '/show/watchlist/%%API_KEY%%' ,args)
    if data == None:
	    print("Error in request from 'getWatchlistMoviesFromTrakt()'")
    return data

def addShowstoWatchList(imdbList):
    args = {}
    shows = []
    for imdbShow in imdbList:
        show = {}
        show['imdb_id'] = imdbShow['imdb_id']
        shows.append(show)
    args['shows'] = shows
    data = traktJsonRequest('POST', '/show/watchlist/%%API_KEY%%' ,args)
    if data == None:
	    print("Error in request from 'addShowstoWatchList()'")
    return data

def addMovietoWatchlist(imdbid):
    args = {}
    movies = []
    movie = {}
    movie['imdb_id'] = imdbid
    movies.append(movie)
    args['movies'] = movies
    data = traktJsonRequest('POST', '/movie/watchlist/%%API_KEY%%' ,args)
    if data == None:
	    print("Error in request from 'addMovietoWatchlist()'")
    return data

def addMoviestoWatchlist(imdbList):
    args = {}
    movies = []
    movie = {}
    for imdbMovie in imdbList:
        movie['imdb_id'] = imdbMovie['imdb_id']
        movies.append(movie)
    args['movies'] = movies
    data = traktJsonRequest('POST', '/movie/watchlist/%%API_KEY%%' ,args)
    if data == None:
	    print("Error in request from 'addMovietoWatchlist()'")
    return data


def removeMoviefromWatchlist(imdbid):
    args = {}
    movies = []
    movie = {}
    movie['imdb_id'] = imdbid
    movies.append(movie)
    args['movies'] = movies
    data = traktJsonRequest('POST', '/movie/unwatchlist/%%API_KEY%%' ,args)
    if data == None:
	    print("Error in request from 'removeMoviefromWatchlist()'")
    return data


def dismissMovie(imdbid):
	args = {}
	args['imdb_id'] = imdbid
	data = traktJsonRequest('POST', '/recommendations/movies/dismiss/%%API_KEY%%' , args)
	return data


def getTrendingMoviesFromTrakt():
    data = traktJsonRequest('GET', '/movies/trending.json/%%API_KEY%%')
    if data == None:
        print("Error in request from 'getTrendingMoviesFromTrakt()'")
    return data

def getTrendingShowsFromTrakt():
    data = traktJsonRequest('POST', '/shows/trending.json/%%API_KEY%%')
    if data == None:
        print("Error in request from 'getTrendingMoviesFromTrakt()'")
    return data


def getShowsCalendarFromTrakt(mydate):
    data = traktJsonRequest('POST', '/user/calendar/shows.json/%%API_KEY%%/%%USERNAME%%/{0}/7'.format(mydate))
    if data == None:
        print("Error in request from 'getTrendingMoviesFromTrakt()'")
    return data

def getWatchlistShowsfromTrakt():
    data = traktJsonRequest('POST', '/user/watchlist/shows.json/%%API_KEY%%/%%USERNAME%%')
    if data == None:
        print("Error in request from 'getTrendingMoviesFromTrakt()'")
    return data


def getPremieresCalendarFromTrakt(mydate):
    data = traktJsonRequest('POST', '/calendar/premieres.json/%%API_KEY%%/{0}/7'.format(mydate))
    if data == None:
        print("Error in request from 'getTrendingMoviesFromTrakt()'")
    return data



def getMovieInfobySearch(title):
    title = unicodedata.normalize('NFKD',title).encode('ASCII', 'ignore')
    data = traktJsonRequest('POST', '/search/movies.json/%%API_KEY%%/{0}'.format(title.replace(' ','+')))
    if data == None:
        print("Error in request from 'gettingMovieInfo()'")
    return data

def getShowInfobySearch(title):
    title = unicodedata.normalize('NFKD',title).encode('ASCII', 'ignore')
    data = traktJsonRequest('POST', '/search/shows.json/%%API_KEY%%/{0}'.format(title.replace(' ','+')))
    if data == None:
        print("Error in request from 'gettingShowInfo()'")
    return data

def getMovieInfobyImdbid(imdbid):
    if not imdbid.startswith('tt'): imdbid = 'tt' + imdbid
    data = traktJsonRequest('POST', '/movie/summary.json/%%API_KEY%%/{0}'.format(imdbid))
    if data == None:
        print("Error in request from 'gettingMovieInfo()'")
    #print data
    return data


def getSeasons(tvdb_id):
	seasons = traktJsonRequest('GET', '/show/seasons.json/%%API_KEY%%/{0}'.format(tvdb_id))
	return seasons

def getEpisodes(tvdb_id,season):
	episodes = traktJsonRequest('POST', '/show/season.json/%%API_KEY%%/{0}/{1}'.format(tvdb_id,season))
	return episodes

def getFullShow(tvdb_id):
	fullshow = traktJsonRequest('POST', '/show/summary.json/%%API_KEY%%/{0}/extended'.format(tvdb_id))
	return fullshow

def getRecommendedMoviesFromTraktbyGenre(args):
    data = traktJsonRequest('POST', '/recommendations/movies/%%API_KEY%%', args)
    if data == None:
        print("Error in request from 'getRecommendedMoviesFromTrakt()'")
    return data

def getMovieGenres():
	data = traktJsonRequest('GET', '/genres/movies.json/%%API_KEY%%')
        if data == None:
	    print("Error in request from 'getRecommendedMoviesFromTrakt()'")
	return data

def getShowGenres():
	data = traktJsonRequest('GET', '/genres/shows.json/%%API_KEY%%')
        if data == None:
	    print("Error in request from 'getRecommendedMoviesFromTrakt()'")
	return data

def setShowSeen(tvdbid,season,episode):
	args = {}
	args['tvdb_id'] = tvdbid
	if season == 100 and episode==100:
		data = traktJsonRequest('POST', '/show/seen/%%API_KEY%%', args)
	else:
		episodes=[]
		episodes.append({})
		episodes[0]['season'] = season
		episodes[0]['episode'] = episode
		args['episodes'] = episodes
		data = traktJsonRequest('POST', '/show/episode/seen/%%API_KEY%%', args)
	return data

def setSeen(args):
	data = traktJsonRequest('POST', '/movie/seen/%%API_KEY%%', args)
	if data == None:
		print("Error in request from 'getRecommendedMoviesFromTrakt()'")
	return data

def setRating(args,type):
	data = traktJsonRequest('POST', '/rate/{0}/%%API_KEY%%'.format(type), args)
	if data == None:
		print("Error in request from 'getRecommendedMoviesFromTrakt()'")
	return data

def getWatchedMovies():
	data = traktJsonRequest('GET', '/user/library/movies/watched.json/%%API_KEY%%/%%USERNAME%%')
        if data == None:
	    print("Error in request from 'getRecommendedMoviesFromTrakt()'")
	return data


def getEpisodeInfo(tvdbid,season,episode):
	url = '/show/episode/summary.json/%%API_KEY%%/{0}/{1}/{2}'.format(tvdbid,season,episode)
	data = traktJsonRequest('GET', url)
        if data == None:
	    print("Error in request from 'getRecommendedMoviesFromTrakt()'")
	return data

def getProgress():
    args = {}
    #args['sort'] = 'activity'
    #args['extended'] = 'normal'
    data = traktJsonRequest('GET', '/user/progress/watched.json/%%API_KEY%%/%%USERNAME%%/all/activity/normal')
    if data == None:
        print("Error in request from 'getProgress()'")
    return data

def getList(user,slug):
	data = traktJsonRequest('POST', '/user/list.json/%%API_KEY%%/{0}/{1}'.format(user,slug))
	if data == None:
		print("Error in request from 'getList()'")
	print data
	return data
	