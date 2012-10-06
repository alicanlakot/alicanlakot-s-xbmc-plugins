# 

from xml.dom.minidom import parse, parseString
import urllib2,sys,re
import xbmcplugin
from utils import common
from BeautifulSoup import BeautifulSoup


def getImdbtop250(page):

        response = urllib2.urlopen('http://www.imdb.com/chart/top')
	html = response.read()
	entries = re.findall(r'<tr bgcolor="#(?:e5e5e5|ffffff)" valign="top"><td align="right"><font face="Arial, Helvetica, sans-serif" size="-1"><b>(\d{1,3})\.</b></font></td><td align="center"><font face="Arial, Helvetica, sans-serif" size="-1">(\d\.\d)</font></td><td><font face="Arial, Helvetica, sans-serif" size="-1"><a href="/title/tt(\d{7})/">([^<]+)</a> \((\d{4})\)</font></td><td align="right"><font face="Arial, Helvetica, sans-serif" size="-1">(\d{1,3}(?:,\d{3})*)</font></td></tr>', html)
	page = int(page)
	first = page-1
	pagesize = 25
        for entry in entries[first*pagesize:page*pagesize]:
		number, score, link_number, title, year, votes = entry
		s= '#{0}: {1} r:{2}'.format(number,'{0}',score)
		common.createMovieListItemfromimdbid(link_number,pagesize,s)
	url = sys.argv[0]+'?action=imdbTop250&page=' + str(page+1)
	if page*pagesize < 250:
		common.createListItem('Next ' + str(pagesize),True, url )
	common.endofDir()
        return 

def getImdbRentals():
	entries = getImdbRentalsList()
	for entry in entries:
		link_number,title,year = entry
		common.createMovieListItemfromimdbid(link_number,len(entries))
	common.endofDir()
        return 

def getImdbRentalsList():
	response = urllib2.urlopen('http://www.imdb.com/boxoffice/rentals')
	html = response.read()
	#entries = re.findall(r'<tr align=right><td><b>(\d{1,3})</b>\.</td><td align=center>(\d{1,3})</td><a href="/title/tt(\d{7})/">([^<]+)</a> \((\d{4})\)</b></td><td>(\d{1,3}(?:,\d{3})*)</td></tr>', html)
	entries = re.findall(r'<td align=left><b><a href="/title/tt(\d{7})/">([^<]+)</a> \((\d{4})\)</b></td>',html)
        return entries



def displayIMDBMenu():
	url = sys.argv[0]+'?action='
	common.createListItem("Top 250", True, url+'imdb_Top250&page=1')
	common.createListItem("Top Rentals", True, url+'imdb_TopRentals')
	types = [ 'Oscars' , 'Cannes' ]
	for type in types:
		for year in reversed(xrange(2000,2013)):
			common.createListItem(type + ' ' + str(year)+' (Beta)', True, url+'imdb_Awards&type={0}&year={1}'.format(type,year))
	common.endofDir()
	return

def getImdbAwards(type,year):
	if type == 'Oscars':
		url = 'http://www.imdb.com/event/ev0000003/{0}'.format(year)
	elif type == 'Cannes':
		url = 'http://www.imdb.com/event/ev0000147/{0}'.format(year)
	response = urllib2.urlopen(url)
	html = response.read()
	soup = BeautifulSoup(html)
	#print soup.prettify()
	winners = soup.findAll('h2')
	movies = dict()
	for winner in winners:
	    category = winner.text
	    try:
		    h3 = winner.findNextSibling('blockquote').h3
	    except:
		continue
	    winnerdiv = h3.findNextSibling('div')
	    link = winnerdiv.find(href=re.compile("/title/tt(\d{7})/"))
	    imdb_number = re.match(r'/title/tt(\d{7})/',link.get('href')).group(1)
	    if not imdb_number in movies.keys():
		    movie = common.getMovieInfobyImdbid(imdb_number)
		    if movie:
			    movies[imdb_number] = movie
		    else:
			    movies[imdb_number] = None
	    else:
                    movie= movies[imdb_number]
	    common.createListItem(category, False, '',len(winners)*2)
	    if movie:
		common.createMovieListItemTrakt(movie,len(winners)*2)
	    else:
		common.createListItem(imdb_number, False, '',len(winners)*2)
	common.endofDir()
        return 

def addImdbToLib(fg):
	if fg == 'True':
		common.Notification('Getting:','IMDB Top Rentals')
	totalAdded = 0
	response = urllib2.urlopen('http://www.imdb.com/boxoffice/rentals')
	html = response.read()
	#entries = re.findall(r'<tr align=right><td><b>(\d{1,3})</b>\.</td><td align=center>(\d{1,3})</td><a href="/title/tt(\d{7})/">([^<]+)</a> \((\d{4})\)</b></td><td>(\d{1,3}(?:,\d{3})*)</td></tr>', html)
	entries = re.findall(r'<td align=left><b><a href="/title/tt(\d{7})/">([^<]+)</a> \((\d{4})\)</b></td>',html)
	for entry in entries:
		link_number,title,year = entry
		created = common.createMovieStrm(title,year,'tt'+link_number)
		totalAdded = totalAdded + created
	        common.createMovieNfo(title,year,'tt'+link_number)
        return totalAdded

def imdbAction(params):

	if(params['action'] == 'imdb_Menu'):
		displayIMDBMenu()



	elif(params['action'] == 'imdb_Top250'):
		xbmcplugin.setContent(int(sys.argv[1]), 'movies')
		page = params['page']
		getImdbtop250(page)
	

	elif(params['action'] == 'imdb_TopRentals'):
		xbmcplugin.setContent(int(sys.argv[1]), 'movies')
		getImdbRentals()

	elif(params['action'] == 'imdb_Awards'):
		year = params['year']
		type = params['type']
		xbmcplugin.setContent(int(sys.argv[1]), 'movies')
		getImdbAwards(type,year)
