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
        self.best_quality_result = None
        self.dirindex = -1

    def checkOneClick(self,SR):
        if self.oneclick:
            j,k = settings.getQualitysetting()
            if SR.quality.value >= j and SR.quality.value < k:
                self.best_quality_result = SR
                SR.oneclick = True
            else:
                if (self.best_quality_result==None and SR.quality.value < j):
                    SR.oneclick = False
                    self.best_quality_result = SR
                elif (self.best_quality_result==None and SR.quality.value > j):
                    SR.oneclick = False
                    self.best_quality_result = None
                elif (SR.quality.value > self.best_quality_result.quality.value and SR.quality.value < j):
                    SR.oneclick = False
                    self.best_quality_result = SR
        return

    def quality_options(self):
        return [i.text for i in self.results]

    def fillOptions(self):
        while True:
            SR = self.checkNext()
            if SR == None:
                break

    def oneClickResult(self):
        while True:
            SR = self.checkNext()
            if SR == None:
                break
            if SR.oneclick:
                break
        if self.best_quality_result:
            return self.best_quality_result
        else:
            return None

    def checkNext(self):
        self.dirindex = self.dirindex + 1
        if self.dirindex > len(self.dirs):
            return None
        return self.check()

class SearchResult():
    def __init__(self,myfile,quality,valid):
        self.valid = valid
        self.file = myfile
        self.quality = quality
        self.oneclick = None
        mysize = size(int(myfile['size']))
        self.text = str('[' + mysize + '] '+str(quality) + ' ' + myfile['name'])

    def __repr__(self):
        return self.text

    def mediaUrl(self):
            files = furklib.fileInfo(self.file['info_hash'])
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

class MovieSearch(Search):
    def __init__(self, title,year,oneclick):
        Search.__init__(self)
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
            SR = SearchResult(file,myquality,True)
            self.checkOneClick(SR)
            self.results.append(SR)
            return SR

        else:
            return None


class ShowSearch(Search):
    def __init__(self, title,season,number,oneclick):
        Search.__init__(self)
        self.title = title
        self.season = season
        self.number = number

        self.oneclick = oneclick
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
                SR = SearchResult(file,myquality,True)
                self.checkOneClick(SR)
                self.results.append(SR)
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



