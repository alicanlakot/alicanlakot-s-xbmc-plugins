# 

from xml.dom.minidom import parse, parseString
import urllib2,sys
from utils import common
from utils import settings

def getCriticker():
	apikey = settings.getSetting('criticker_apikey')
	if len(apikey) < 5 :
		common.Notification ('Error','Please set up Criticker key in settings')
		settings.openSettings()
		return
	url = 'http://api.criticker.com/handler.php?CritickerKey=%%API_KEY%%&Function=RecommendFilm'
        url = url.replace("%%API_KEY%%",apikey)
	print url
        req = urllib2.Request(url)
        req.add_header('User-Agent', "%s %s" % (sys.modules[ "__main__" ].__plugin__, sys.modules[ "__main__" ].__version__))
        response = urllib2.urlopen(req)
        dom = parse(response)
        try:
		title = dom.getElementsByTagName("FilmName")[0].firstChild.data
		year = dom.getElementsByTagName("FilmYear")[0].firstChild.data
		avgtier = dom.getElementsByTagName("AvgTier")[0].firstChild.data
	except:
		common.Notification ('Error','Please check your Criticker key in settings')
		settings.openSettings()
		return

	s= '{0} ({1}) r:{2}'.format(title,year,avgtier)
	common.createMovieListItem(s,title,year)
	url = sys.argv[0]+'?action=' 
	common.createListItem('Another',True, url + 'criticker')
	common.endofDir()
        return 

