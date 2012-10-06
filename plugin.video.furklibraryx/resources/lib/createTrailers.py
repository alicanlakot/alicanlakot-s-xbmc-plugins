import urlparse
import urllib
import xbmcgui
import os,time
from sites import traktlib
from sites import imdb
from utils import common
from FileAccess import FileLock, FileAccess
from Globals import *
import sys

PLAYLIST_PATH = sys.modules[ "__main__" ].PLAYLIST_PATH
def getReco(channel):
	filename = PLAYLIST_PATH +  str(channel) + '.m3u'
	if not os.path.isfile(filename):
		refresh=True
	else:
		f = os.path.getmtime(filename)
		if time.time() - f > 1800:
			refresh=True
		else:
			refresh=False
	if refresh==False:
		return refresh
	count= 0
	updateDialog = xbmcgui.DialogProgress()
        updateDialog.create("FurkTrailers", "Receiving Movies from trakt")
	updateDialog.update(25, "Recommended", "Total: " + str(count))
	reco = traktlib.getRecommendedMoviesFromTrakt() 
	count = count + len(reco)
	updateDialog.update(50, "Watchlist", "Total: " + str(count))
	WL = traktlib.getWatchlistMoviesFromTrakt() 
	count = count + len(WL)
	updateDialog.update(75, "Trending", "Total: " + str(count))
	trending= traktlib.getTrendingMoviesFromTrakt()
	count = count + len(trending)
	
	updateDialog.update(99, "Imdb", "")
	imdbTop = []
	entries = imdb.getImdbRentalsList()
	for entry in entries:
		link_number,title,year = entry
		movie = common.getMovieInfobyImdbid(link_number)
		imdbTop.append(movie)
	updateDialog.update(99, "Imdb", "Len: " + str(len(entries)))
	updateDialog.close()

	if count==0:
		return
	
	movies = []
	if trending:
		movies= movies + trending
	if WL:
		movies= movies + WL
	if reco:
		movies = movies + reco
	if len(imdbTop)>0:
		movies = movies + imdbTop
	if len(movies)>0:
		fle = FileAccess.open(filename, 'w')
		flewrite = "#EXTM3U\n"
		for movie in movies:
			try:
				watched = movie['watched']
			except:
				watched = False
			try:
				inwatchlist= movie['in_watchlist']
			except:
				inwatchlist = False

			if movie['trailer']=='':
				continue
			if watched == True and inwatchlist == False:
				continue
			if movie in reco:
				type = 'Recommended'
			elif movie in imdbTop:
				type= 'Imdb Top Rentals'
			elif movie in WL:
				type= 'In Watchlist'
			elif movie in trending:
				if int(movie['watchers'])<2:
					continue
				else:
					type = 'Trending ' + str(movie['watchers']) + ' watchers'
			mygenre = ''
			try:
				for genre in movie['genres']:
					mygenre = mygenre + genre + ' / '
				if len(mygenre)>0:
					mygenre = mygenre[:-2] 
			except:
				pass


			# #EXTINF:5760,2 Days In Paris////Adam Goldberg delivers "an uproarious study in transatlantic culture panic" as Jack, an anxious, hypochondriac-prone New Yorker vacationing throughout Europe with his breezy, free-spirited Parisian girlfriend, Marion. But when they make a two-day stop in Marion's hometown, the couple's romantic trip takes a turn as Jack is exposed to Marion's sexually perverse and emotionally unstable family.
			tmpstr = str(movie['runtime']*60) + ','
			tmpstr = str(50) + ','
			try:
				imdbid= movie['imdb_id'].encode('utf-8').strip()
			except:
				imdbid= ''
			try:
				rating = str(movie['ratings']['percentage']/10.0) + ' ' + type + ' ' + mygenre.encode('utf-8').strip()
			except:
				rating = type
			poster= urllib.quote(movie['images']['poster'][7:])
			tmpstr += movie['title'].encode('utf-8').strip() + " (" + str(movie['year']) +  ")//" + rating + "//" + poster + "//" + imdbid + "//" + movie['overview'].encode('utf-8').strip()  
			tmpstr = tmpstr[:600]
			tmpstr = tmpstr.replace("\\n", " ").replace("\\r", " ").replace("\\\"", "\"")
			tmpstr = tmpstr + '\n' + getTrailer(movie['trailer']).encode('utf-8').strip()

			flewrite += "#EXTINF:" + tmpstr + "\n"
			#print movie
		
		fle.write(flewrite)
		fle.close()
		return refresh


def getTrailer(path):
	url_data = urlparse.urlparse(path)
	query = urlparse.parse_qs(url_data.query)
	video_id = query["v"][0]
	url = "plugin://plugin.video.youtube/?action=play_video&videoid=%s" %video_id
	return url
