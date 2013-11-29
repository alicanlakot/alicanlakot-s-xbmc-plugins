import json
import httplib
import datetime
import os
import urllib
import urllib2
from xml.dom.minidom import Document
import hashlib
from utils import settings


headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}



# get a connection to trakt


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
def furkJsonRequest(method, req, args={}, returnStatus=False, anon=False, conn=False, silent=False, passVersions=False):
    apikey = settings.getSetting('furk_apikey')
    if settings.getSetting('proxy')=="false":
        myproxy={}
    else:
        proxy = urllib2.ProxyHandler({'http':'http://proxyinternet.frlev.danet:80','https':'https://proxyinternet.frlev.danet:80'})
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)

    req = 'https://www.furk.net/api/' + req
    req = req.replace("%%API_KEY%%",apikey)


    raw = urllib2.urlopen(req).read()

    data = json.loads(raw)

    if 'status' in data:
        if data['status'] == 'error':
            print("traktQuery: Error: " + str(data['error']))
            if returnStatus:
                return data
            if not silent: notification("Furk Library", str(data['error'])) # Error
	    login(settings.getSetting('furk_login'),settings.getSetting('furk_password'))
            return data

    return data

# returns list of movies from watchlist

def searchFurk(query):
    data = furkJsonRequest('GET', 'plugins/metasearch?api_key=%%API_KEY%%&q={0}&limit=50'.format(urllib.quote(query)))
    if data == None:
        print("Error in request from 'searchFurk'")
	return None
    try:
        return data['files']
    except:
	return None


def myFeeds():
    data = furkJsonRequest('GET', 'feed/get?api_key=%%API_KEY%%')

    if data == None:
        print("Error in request from 'searchFurk'")
        return None
    try:
        return data
    except:
        return None

def addFeed(name):
    name = format(urllib.quote(name))
    data = furkJsonRequest('GET', 'feed/add?api_key=%%API_KEY%%&name={0}&url={0}'.format(name))
    if data == None:
        print("Error in request from 'searchFurk'")
        return None
    try:
        return data
    except:
        return None


def myFiles(name=None):
    if not name:
        data = furkJsonRequest('GET', 'file/get?api_key=%%API_KEY%%')
    else:
        name = urllib.quote(name)
        data = furkJsonRequest('GET', 'file/get?api_key=%%API_KEY%%&name_like={0}'.format(name))

    if data == None:
        print("Error in request from 'searchFurk'")
        return None
    if data['found_files']>0:
        return data['files']
    else:
        return None



def fileInfo(hash):
    data = furkJsonRequest('GET', 'file/info?api_key=%%API_KEY%%&info_hash={0}&t_files=1'.format(hash))
    if data == None:
        print("Error in request from 'getWatchlistMoviesFromTrakt()'")
	return None
    return data['files'][0]['t_files']

def notification(title, message):
        try:
                xbmc.executebuiltin("XBMC.Notification("+title+","+message+")")
                print message.encode("utf-8")
        except: pass
        return


def login(username,password):
	url= 'http://api.furk.net/api/login/login'
	values = {'login':username, 'pwd': password}
	data = urllib.urlencode(values)
	req = urllib2.Request(url, data)
	resp = urllib2.urlopen(req)
	out = json.loads(resp.read())
	#notification ('output' , out['api_key'])
	try:
		settings.setSetting('furk_apikey',out['api_key'])
		notification ('Login to Furk succesful for' , username)
	except:
		notification ('output' , out)

