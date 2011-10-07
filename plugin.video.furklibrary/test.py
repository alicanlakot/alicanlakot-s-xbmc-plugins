import sys, urllib
from resources.lib.utils.titles.movie import MovieParser
# Plugin constants
__plugin__ = 'Furk.net Library'
__author__ = 'Gpun Yog'
__url__ = 'http://www.furk.net/t/xbmc'
__version__ = '1.0.0'

if __name__ == "__main__":
    from resources.lib import getter, printer
    dirs = getter.getDirs()
    for d in dirs:
        id = d.getElementsByTagName('id').item(0).firstChild.data
        name = d.getElementsByTagName('name').item(0).firstChild.data
        date = d.getElementsByTagName('date').item(0).firstChild.data
        thumb = d.getElementsByTagName('thumb').item(0).firstChild.data
        files = getter.getFiles(id)
        printer.addFiles(files)
                                
