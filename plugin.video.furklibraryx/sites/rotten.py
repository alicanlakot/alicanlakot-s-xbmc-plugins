import json
import httplib
import os,sys
import unicodedata
from xml.dom.minidom import Document
from utils import settings
from utils import common
#/api/public/v1.0/lists/dvds/current_releases.json?page_limit=16&page=1&country=us&apikey=
# Trakt
apikey = 'cn6g7mzgatbfaxvza35nyjf8'
headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
# End Trakt


def testUser(username,pwd):
	data = traktJsonRequest('POST', '/account/test/%%API_KEY%%',args = {},returnStatus=True)
	if data == None:
		print("Error in request from 'getTrendingMoviesFromTrakt()'")
	return data



# get a connection to rotten
def getTraktConnection():
    conn = httplib.HTTPConnection('api.rottentomatoes.com')
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
    #req = 'http://api.rottentomatoes.com' + req
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

def showCurrentReleaseDvds():
	results = traktJsonRequest('GET', '/api/public/v1.0/lists/dvds/current_releases.json?apikey=%%API_KEY%%')
	movies = results['movies']
	showMovies(movies)
	
def rottenCommon(url):
	results = traktJsonRequest('GET', url+'?apikey=cn6g7mzgatbfaxvza35nyjf8' )
	movies = results['movies']
	showMovies(movies)


def showMovies(movies):
	for movie in movies:
		try:
			imdbid = movie['alternate_ids']['imdb']
		except:
			imdbid = None
		if imdbid:
			common.createMovieListItemfromimdbid(imdbid,totalItems = len(movies))
		else:
			movietitle = movie['title']
			movieyear = movie['year']
			createMovieListItemTrakt(None,movietitle,movieyear,totalItems = len(movies))
	common.endofDir()

def displayRottenMenu():
	url = sys.argv[0]+'?action=rotten_common'
	results = traktJsonRequest('GET', 'http://api.rottentomatoes.com/api/public/v1.0/lists/dvds.json?apikey=cn6g7mzgatbfaxvza35nyjf8')
	print results
	links = results['links']
	for link in links:
		linktxt = getCamelCase(link).replace('_',' ')
		common.createListItem(linktxt, True, url+'&url='+links[link])
	common.endofDir()

def rottenAction(params):
	if(params['action'] == 'rotten_Menu'):
		displayRottenMenu()
	
	elif(params['action'] == 'rotten_CurrentReleaseDvds'):
	        # Search
		rottenCommon('api.rottentomatoes.com/api/public/v1.0/lists/dvds/top_rentals.json?apikey=cn6g7mzgatbfaxvza35nyjf8')
	elif(params['action'] == 'rotten_common'):
		rottenCommon(params['url'])
	else:
		common.Notification('Action Not found:' , params['action'])

def getCamelCase(s, sep=' '):
	return ''.join([t.title() for t in s.split(sep)])