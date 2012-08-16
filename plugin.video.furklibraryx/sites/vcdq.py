from ext import feedparser
from ext.titles.movie import MovieParser
from utils import common

def getVCDQ(url):

	d = feedparser.parse( url )
	common.Notification("Navigating to ",d['feed']['title'])
	mylist= list()




        for span in d.entries:
            rssname = span.title
	    myPlot = span.description
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
	    if s in mylist:
		continue
	    else:
	        common.createMovieListItem(s,myName,myYear,len(d.entries))
		mylist.append(s)
		
        common.endofDir()
        return
