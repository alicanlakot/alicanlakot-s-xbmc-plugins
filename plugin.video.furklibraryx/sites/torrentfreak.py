from ext import feedparser
from ext.titles.movie import MovieParser
from utils import common
import re

def getpopular(url):

	d = feedparser.parse( url )
	mylist= list()
	html = d.entries[0]['content'][0]['value'].replace('\n','')
	entries = re.findall(r'<a href="http://www.imdb.com/title/tt(\d{7})/">',html)
	for entry in entries:
		imdbid = entry
		common.createMovieListItemfromimdbid(imdbid,len(entries))
	common.endofDir()
        return
