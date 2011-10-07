'''
    Furk.net player / scraper for XBMC
    Copyright (C) 2011 Alican Lakot

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys, urllib, time
import xbmc, xbmcaddon, xbmcgui, xbmcplugin


# Plugin constants
__plugin__ = 'Furk.net Library'
__author__ = 'Alican Lakot'
__url__ = 'http://www.furk.net/?INVITE=1216084'
__version__ = '1.0.2'
__settings__ = xbmcaddon.Addon(id='plugin.video.furklibrary')
ADDON = xbmcaddon.Addon(id='plugin.video.furklibrary')

print "[PLUGIN] '%s: version %s' initialized!" % (__plugin__, __version__)


def parse_qs(u):
	params = '?' in u and dict(p.split('=') for p in u[u.index('?') + 1:].split('&')) or {}
	
	return params;

###################
### Auto-update ###
###################

def AutoUpdateLibrary():

	
	print "FurkLibrary running an automatic update"
	
	if ADDON.getSetting('auto_update') == "true":
		xbmc.executebuiltin('CancelAlarm(updateFurklibrary)')

	timer_amounts = {}
	timer_amounts['0'] = '60'
	timer_amounts['1'] = '120'
	timer_amounts['2'] = '300'
	timer_amounts['3'] = '600'
	timer_amounts['4'] = '900'
	timer_amounts['5'] = '1440'

	#only do this if we are not playing anything
	if xbmc.Player().isPlaying() == False:
                pxDialog = xbmcgui.DialogProgress()
                ret = pxDialog.create('XBMC', 'Getting dirs...','Please wait')
                dirs = getter.getDirs()
                pxDialog.close()
		if dirs:
                        collector.collect(dirs)
                        xbmc.executebuiltin('UpdateLibrary(video)')
		
	#reset the timer
	if ADDON.getSetting('auto_update') == "true":
		xbmc.executebuiltin('AlarmClock(updateFurklibrary,XBMC.RunScript(special://home/addons/plugin.video.furklibrary/default.py,0,action="AU"),' + timer_amounts[ADDON.getSetting('update_timer')] + ',False)')

	print "FurkLibrary update complete"
	return;


from resources.lib import getter, printer, collector


##xbmc.log('params_str=%s' % sys.argv[2])       
params = parse_qs(sys.argv[2])
if not params:
        params['action'] = 'dirs'
xbmc.log('_params=%s' % params) 


if(params['action'] == 'files'):
        # Enter a directory | open torrent and list files
        files = getter.getFiles(params['did'])
        collector.printFiles(files,params['did'])

elif(params['action'] == 'play'):
        # Play a file
        printer.playFile(params['url'])

elif(params['action'] == 'about'):
        # Play a file
	collector.Notification(__plugin__,__version__)


elif(params['action'] == 'recent_queries'):
        # Show previous searches
        printer.printRecentQueries()
        
elif(params['action'] == 'AU'):
        # Autoupdate
        AutoUpdateLibrary()

elif(params['action'] == 'DeleteHistory'):
        # Autoupdate
        collector.DeleteHistory()

elif(params['action'] == 'search_test'):
        # Search
        dirs = getter.searchDirs('xxx')
        printer.printDirs(dirs)

elif(params['action'] == 'search'):
        # Search
        keyboard = xbmc.Keyboard(urllib.unquote(params['query']), 'Search')
        keyboard.doModal()

        if keyboard.isConfirmed():
                query = keyboard.getText()
                dirs = getter.searchDirs(query)
                printer.printDirs(dirs)

elif(params['action'] == 'scrapeDir'):
        did = params['did']
        collector.Notification("Scraping" , " files")
        files = getter.getFiles(did)
	scraped = collector.addFiles(did,files)
	collector.Notification("Scraped",str(scraped) + " files")
        xbmc.executebuiltin('UpdateLibrary(video)')
        

elif(params['action'] == 'playMe'):
        # Player
        did = params['did']
        fid = params['fid']
        name = params ['name']
        play_url = collector.playMe(did,fid,name)
        if play_url:
                #xbmc.Player().play(play_url)
		collector.Notification("Found"," and playing!")
		time.sleep(1)
                listitem = xbmcgui.ListItem(name, iconImage="DefaultVideoBig.png", thumbnailImage='', path=play_url)
	        listitem.setLabel(name)
		listitem.setProperty("IsPlayable", "true")
		xbmcplugin.setResolvedUrl(int(sys.argv[ 1 ]),True,listitem)
		#time.sleep(20)
        else:
                name = '@Search...'
                url = sys.argv[0] + '?action=search&query='
                xbmcplugin.setResolvedUrl(int(sys.argv[ 1 ]),False,xbmcgui.ListItem())
        #collector.Notification("hello","mello")
        
elif(params['action'] == 'playMenow'):
        # Player
        did = params['did']
        fid = params['fid']
        name = ''
        play_url = collector.playMe(did,fid,name)
        if play_url:
                #xbmc.Player().play(play_url)
		collector.Notification("Found"," and playing!")
		time.sleep(1)
                listitem = xbmcgui.ListItem(name, iconImage="DefaultVideoBig.png", thumbnailImage='', path=play_url)
	        listitem.setLabel(name)
		listitem.setProperty("IsPlayable", "true")
		xbmc.Player().play(urllib.unquote(play_url), listitem)
		#time.sleep(20)
        else:
                collector.Notification("hello","mello")

else:
        # torrents a root Directories 
        xbmc.log('argv=%s' % sys.argv)
        collector.AddonMenu()
                

print 'Closing FurkLib'
#sys.modules.clear()
