#

from xml.dom.minidom import parse, parseString
import sys,re,urllib
from ext import requests
from utils import regex_from_to,regex_get_all,get_url

def watchlist_imdb(url,start):
    movies = []
    body = get_url(url, cache=".")
    all_tr = regex_get_all(body, '<tr data-item', '</tr>')

    for tr in all_tr:
        all_td = regex_get_all(tr, '<td', 'td>')
        imdb_id = regex_from_to(all_td[1], 'title/', '/')
        name = regex_from_to(all_td[1], '/">', '</a>')
        year = regex_from_to(all_td[2], 'year">', '</td>')
        try:
            rating = regex_from_to(all_td[6], 'user_rating">', '</')
            votes = regex_from_to(all_td[7], 'num_votes">', '</')
        except:
            rating = ""
            votes = ""
        movies.append({'imdb_id': imdb_id, 'name': name, 'year': year, 'rating': rating, 'votes': votes})
    p_start = int(start) + 250
    p_end = (int(start) + (250 * 2)) -1
    #movies.append({'imdb_id': str(pname), 'name': '[COLOR gold]' + "%s (%s-%s)" % (">>> Next Page",str(p_start),str(p_end)) + '[/COLOR]', 'year': "rem", 'rating': start, 'votes': "NW"})
    return movies


def watchlist_movies(watchlist_url,start):
    params = {}
    nstart = str(int(start) + 250)
    params["title_type"] = "feature,documentary,tv_movie"
    params["start"] = start
    params["view"] = 'compact'
    url = "%s%s%s" % (watchlist_url, urllib.urlencode(params),"&sort=listorian:asc")
    movies = watchlist_imdb(url,start)
    return movies

def watchlist_shows(watchlist_url,start):
    params = {}
    nstart = str(int(start) + 250)
    params["title_type"] = "tv_series,mini_series,tv_special"
    params["start"] = start
    params["view"] = 'compact'
    url = "%s%s%s" % (watchlist_url, urllib.urlencode(params),"&sort=listorian:asc")
    tv_shows = watchlist_imdb(url,start)
    return tv_shows




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
