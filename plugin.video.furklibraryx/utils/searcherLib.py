'''
Created on Nov 29, 2013

@author: altasak
'''
from ext.hurry.filesize import size
from sites import furklib
from utils import functions,settings
from ext.titles.series import SeriesParser
from ext.titles.movie import MovieParser
from ext.titles.parser import TitleParser, ParseWarning
import re,unicodedata



class Search():
    def __init__(self):
        self.valids = 0
        self.results = []
        self.qualities = []
        self.best_quality_result = None
        self.oneClickSatisfied = False
        self.dirindex = -1
        self.mediatype = None



    def quality_options(self):
        return [i.text for i in self.results]

    def fillOptions(self):
        while True:
            SR = self.checkNext()
            if self.oneClickSatisfied == True:
                break
            if SR == None:
                break

    def oneClickResult(self):
        self.best_quality_result


    def checkNext(self):
        self.dirindex = self.dirindex + 1
        if self.dirindex > len(self.dirs):
            return None
        return self.check()

class SearchResult():
    def __init__(self,search,mydir,quality,valid,myurl=None):
        self.search = search
        self.valid = valid
        self.dir = mydir
        self.quality = quality
        mysize = size(int(mydir['size']))
        self.myUrl = myurl
        self.text = '[{0}] {1} {2} {3}'.format(mysize,quality.value,str(quality),mydir['name'])
        self.search.results.append(self)
        if not self.quality in self.search.qualities:
            self.search.qualities.append(self.quality)
        self.checkOneClick()
        #if self.search.best_quality_result == None:
            #self.search.best_quality_result = self
    def __repr__(self):
        return self.text



    def mediaUrl(self):
        if self.myUrl:
            return self.myUrl
        else:
            files = furklib.fileInfo(self.dir['info_hash'])
            for f in files:
                myname = f['name']
                #print myname
                if 'sample' in myname.lower():
                    continue
                if myname.endswith('avi') or myname.endswith('mkv') or myname.endswith('mp4'):
                    return f['url_dl']
                    break
                else:
                    continue
            return None

    def checkOneClick(self):
        if self.search.oneclick:
            j,k = settings.getQualitysetting()
            if self.quality.value >= j and self.quality.value < k:
                self.search.best_quality_result = self
                self.search.oneClickSatisfied = True
            else:
                if (self.search.best_quality_result==None and self.quality.value < j):
                    self.search.best_quality_result = self
                elif (self.search.best_quality_result==None and self.quality.value > j):
                    self.search.best_quality_result = None
                elif (self.quality.value > self.search.best_quality_result.quality.value and self.quality.value < j):
                    self.search.best_quality_result = self
        return
class MovieSearch(Search):
    def __init__(self, title,year,oneclick):
        Search.__init__(self)
        self.mediatype = 'Movie'
        self.title = title.encode("utf-8")
        self.year = year
        self.oneclick = oneclick
        if year==0:
            query = '{0} -cam'.format(title)
        else:
            query = '{0} {1} -cam'.format(title,year)

        self.dirs = furklib.searchFurk(query)

    def check(self):
        file = self.dirs[self.dirindex]
        if file['is_ready']=='0':
            return
        id = file['info_hash']
        dirname = file['name']
        valid = False
        parser = MovieParser()
        parser.data = dirname
        parser.parse()
        myName = parser.name
        myYear = parser.year
        myquality = parser.quality
        movie_name =  str(myquality) + ' ' + dirname
        movie_name2 = str(myquality) + ' ' + self.title.strip() + ' (' + str(self.year) + ')'

        if self.year==0 and self.title.lower() in myName.lower():
            valid = True
        if not myYear:
            myYear = 0
            valid = False

        title = unicodedata.normalize('NFKD',unicode(self.title,'utf-8')).encode('ASCII', 'ignore')
        #print 'T:' + title.lower()
        #print 'M:' + myName.lower()
        if title.lower() in myName.lower() and myquality.value>250:
            valid = True

        if valid:
            self.valids += 1
            SR = SearchResult(self,file,myquality,True)
            return SR

        else:
            return None


class ShowSearch(Search):
    def __init__(self, title,season,number,oneclick):
        Search.__init__(self)
        self.title = title
        self.season = int(season)
        self.number = int(number)
        self.oneclick = oneclick
        self.mediatype = 'Show'
        query = '''{0} S{1:0>2}E{2:0>2}'''.format(self.title, self.season, self.number)
        self.dirs = furklib.searchFurk(query)

    def check(self):
        file = self.dirs[self.dirindex]
        if file['is_ready']=='0':
            return
        id = file['info_hash']
        dirname = file['name']

        myParser= self.guess_series(dirname)
        if myParser:
            myParser.parse()
            myName = myParser.name
            mySeason = myParser.season
            myNumber = myParser.episode
            myYear = 0
            myNametoCheck = functions.CleanFileName(myName).lower().replace(' ','')
            titletoCheck = functions.CleanFileName(self.title).lower().replace(' ','')
            if myParser.quality: myquality = myParser.quality
            movie_name = '''{0} {1} S{2:0>2}E{3:0>2}'''.format(myquality,myNametoCheck, mySeason, myNumber)
            if int(mySeason) <> int(self.season):
                return
            elif titletoCheck == myNametoCheck and int(mySeason)==int(self.season) and int(myNumber)==int(self.number) and myquality.value>0:
                valid = True
            if valid:
                self.valids += 1
                SR = SearchResult(self,file,myquality,True)
                return SR

    def guess_series(self,title):
        """Returns a valid series parser if this :title: appears to be a series"""
        #print 'title=' + title.encode("utf-8")
        parser = SeriesParser(identified_by='ep', allow_seasonless=False)
        # We need to replace certain characters with spaces to make sure episode parsing works right
        # We don't remove anything, as the match positions should line up with the original title
        clean_title = re.sub('[_.,\[\]\(\):]', ' ', title)
        match = parser.parse_episode(clean_title)
        if match:
            if parser.parse_unwanted(clean_title):
                return
            elif match['match'].start() > 1:
                # We start using the original title here, so we can properly ignore unwanted prefixes.
                # Look for unwanted prefixes to find out where the series title starts
                start = 0
                prefix = re.match('|'.join(parser.ignore_prefixes), title)
                if prefix:
                    start = prefix.end()
                # If an episode id is found, assume everything before it is series name
                name = self.title[start:match['match'].start()]
                # Remove possible episode title from series name (anything after a ' - ')
                name = name.split(' - ')[0]
                # Replace some special characters with spaces
                name = re.sub('[\._\(\) ]+', ' ', name).strip(' -')
                # Normalize capitalization to title case
                name = name.title()
                # If we didn't get a series name, return
                if not name:
                    return
                parser.name = name
                parser.data = title

                try:
                    parser.parse(data=title)
                except ParseWarning, pw:
                    pass
                    #common.Notification('ParseWarning:' , pw.value)
                if parser.valid:
                    return parser

    def deepsearch(self):
        dir_names = []
        dir_ids = []
        season_episode = "s%.2de%.2d" % (self.season, self.number)
        season_episode2 = "%d%.2d" % (self.season, self.number)

        tv_show_season = "%s season" % self.title
        tv_show_episode = "%s %s" % (self.title, season_episode)

        dirs2 = []
        dirs2.extend(furklib.myFiles(self.title))
        try:
            dirs2.extend(furklib.searchFurk(tv_show_episode))
        except:
            pass
        try:
            dirs2.extend(furklib.searchFurk(tv_show_season))
        except:
            pass
        try:
            dirs2.extend(furklib.searchFurk(self.title))
        except:
            pass
        for d in dirs2:
            if self.valids>0:
                continue
            if d['is_ready']=='0':
                continue
            if not (d['name'].lower().startswith(self.title.lower())):
                continue
            dir_names.append(d['name'])
            dir_ids.append(d['info_hash'])


        if len(dir_names)>0:
            idx = 0
            for dirname in dir_names:
                id = dir_ids[idx]
                idx = idx + 1
                self.filebyfile(id,dirname)
        else:
            pass

    def filebyfile(self,id,dirname):
        valid = False
        title = re.sub(r'\([^)]*\)', '', self.title)
        titletoCheck = functions.CleanFileName(title).lower().replace(' ','')

        #print 'Dir:{0}'.format(dirname)
        files = furklib.fileInfo(id)
        if not files:
            return

        for f in files:
            if self.oneClickSatisfied:
                break
            if len(self.qualities) >= 3 :
                break
            name = f['name']
            path = f['path'].replace('/',' ')
            mysize = size(int(f['size']))
            if 'sample' in name.lower() or 'subs' in name.lower():
                continue
            play_url = f['url_dl']
            valid = False
            myquality = 'unknown Akin'
            myParser= self.guess_series(name)
            if not myParser:
                myParser= self.guess_series(title + ' ' + name)
            if not myParser:
                myParser= self.guess_series(title + ' ' + path + name)
            movie_name = dirname + ' ' + path + name
            if myParser:
                try:
                    myParser.parse()
                except:
                    continue
                myName = myParser.name
                mySeason = myParser.season
                myNumber = myParser.episode
                myYear = 0
                if myParser.quality: myquality = myParser.quality
                myNametoCheck = functions.CleanFileName(myName).lower().replace(' ','')

                movie_name = '''{0} {1} S{2:0>2}E{3:0>2}'''.format(myquality,myName, mySeason, myNumber)
                movie_name2 = '''B:{0} {1} S{2}E{3}'''.format('unk',title, self.season, self.number)
                clean_name = '''{1} S{2:0>2}E{3:0>2}'''.format(myquality,myName, mySeason, myNumber)
                #print 'U: {0} S{1}E{2}'.format(myNametoCheck,mySeason,myNumber)
                #print 'Y: {0} S{1}E{2}'.format(titletoCheck,season,number)
                if not myNametoCheck.startswith(titletoCheck):
                    #print 'break namecheck'
                    break
                if int(mySeason)==self.season and int(myNumber)==self.number:
                    valid= True

            if valid:
                self.valids += 1
                SR = SearchResult(self,f,myquality,True,play_url)
                break
            else:
                continue
        return






