import urllib2,sys
from ext.BeautifulSoup import BeautifulSoup
from utils import common
import urllib

def getMovieLens(url):

        req = urllib2.Request(urllib.unquote(url))
        req.add_header('User-Agent', "%s %s" % (sys.modules[ "__main__" ].__plugin__, sys.modules[ "__main__" ].__version__))
        response = urllib2.urlopen(req)
        soup = BeautifulSoup(response)
        mySpans= soup.findAll('span',attrs={"class" : "movieTitle"})
	##mySpans = mySpans[1], mySpans[2]
        

        for span in mySpans:

            s = span.a.string
            year = s[len(s)-7 : len(s)]
            year = year.replace('(','').replace(')','')
	    year = year.strip()
            title = s.split('(',1)[0].strip()
            title = title.replace(', The','')   		
	    common.createMovieListItem(s,title,year,len(mySpans))


	


        return 

def displayMovieLensmenu():
	url = sys.argv[0]+'?action=movielensUrl&url='
	url1 = url + urllib.quote("http://movielens.org/")
	name1 = 'A'
	url2 = url + urllib.quote("http://movielens.org/")
	name2 = 'Your Wishlist'
	url3 = url + urllib.quote("http://movielens.org/")
	name3 = 'New DVDs'
	urls = []
	urls.append ((url1,name1))
	urls.append ((url2,name2))
	urls.append ((url3,name3))
	for myurl,myname in urls:
		common.createListItem(myname, True, myurl)
	common.endofDir()
	return