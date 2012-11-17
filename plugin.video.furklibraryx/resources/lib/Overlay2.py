#   Copyright (C) 2011 Jason Anderson
#
#
# This file is part of FurkTrailers.
#
# FurkTrailers is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# FurkTrailers is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with FurkTrailers.  If not, see <http://www.gnu.org/licenses/>.

import xbmc, xbmcgui, xbmcaddon
import subprocess, os
import time, threading
import datetime
import sys, re
import random, traceback
from utils import settings

from xml.dom.minidom import parse, parseString

#from Playlist import Playlist
from Globals import *
#from Channel import Channel
#from EPGWindow import EPGWindow
#from ChannelList import ChannelList
#from ChannelListThread import ChannelListThread
from FileAccess import FileLock, FileAccess
#from Migrate import Migrate
import createTrailers
PLAYLIST_PATH = sys.modules[ "__main__" ].PLAYLIST_PATH

class MyPlayer(xbmc.Player):
    def __init__(self):
        xbmc.Player.__init__(self, xbmc.PLAYER_CORE_AUTO)
        self.stopped = False
        self.ignoreNextStop = False


    def log(self, msg, level = xbmc.LOGDEBUG):
        log('Player: ' + msg, level)


    def onPlayBackStopped(self):
        if self.stopped == False:
            self.log('Playback stopped')

            if self.ignoreNextStop == False:
                if self.overlay.sleepTimeValue == 0:
                    self.overlay.sleepTimer = threading.Timer(1, self.overlay.sleepAction)

                self.overlay.background.setVisible(True)
                self.overlay.sleepTimeValue = 1
                self.overlay.startSleepTimer()
                self.stopped = True
            else:
                self.ignoreNextStop = False



# overlay window to catch events and change channels
class TVOverlay(xbmcgui.WindowXMLDialog):
    def __init__(self,*args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)
        self.log('__init__')
        # initialize all variables
        self.channels = []
        self.Player = MyPlayer()
        self.Player.overlay = self
        self.inputChannel = -1
        self.channelLabel = []
        self.lastActionTime = 0
        self.actionSemaphore = threading.BoundedSemaphore()
        self.setCoordinateResolution(1)
        self.timeStarted = 0
        self.infoOnChange = True
        self.infoOffset = 0
        self.invalidatedChannelCount = 0
        self.showingInfo = False
        self.showChannelBug = False
        self.notificationLastChannel = 0
        self.notificationLastShow = 0
        self.notificationShowedNotif = False
        self.isExiting = False
        self.maxChannels = 0
        self.notPlayingCount = 0
        self.ignoreInfoAction = False
        self.shortItemLength = 60
        self.runningActionChannel = 0
	self.showNextItem = True
	self.sleepTimeValue = 0
	self.backgroundUpdating = 2
        self.doModal()
        self.log('__init__ return')


    def resetChannelTimes(self):
        for i in range(self.maxChannels):
            self.channels[i].setAccessTime(self.timeStarted - self.channels[i].totalTimePlayed)


    def onFocus(self, controlId):
        pass


    # override the doModal function so we can setup everything first
    def onInit(self):
        self.log('onInit')

        self.background = self.getControl(101)
        self.getControl(102).setVisible(False)
        self.background.setVisible(True)
        self.currentIdx=settings.getSetting('last_trailer')
	if self.currentIdx=='':
		self.currentIdx =0
        

        self.playerTimer = threading.Timer(2.0, self.playerTimerAction)
        self.playerTimer.name = "PlayerTimer"
        self.infoTimer = threading.Timer(5.0, self.hideInfo)
        #self.myEPG = EPGWindow("script.FurkTrailers.EPG.xml", ADDON_INFO, "default")
        #self.myEPG.MyOverlayWindow = self
        # Don't allow any actions during initialization
        self.actionSemaphore.acquire()
        
	
	# Akin
        refresh = createTrailers.getReco(1)
       	if refresh:
               self.currentIdx=0
        self.timeStarted = time.time()
        self.notificationTimer = threading.Timer(NOTIFICATION_CHECK_TIME, self.notificationAction)
        self.currentChannel = 1
        self.setChannel(self.currentChannel)
        self.background.setVisible(False)
        self.startNotificationTimer()
        self.playerTimer.start()



        self.actionSemaphore.release()
        self.log('onInit return')


    # setup all basic configuration parameters, including creating the playlists that
    # will be used to actually run this thing
    def readConfig(self):
        self.log('readConfig')
        # Sleep setting is in 30 minute incriments...so multiply by 30, and then 60 (min to sec)
        self.sleepTimeValue = int(REAL_SETTINGS.getSetting('AutoOff')) * 1800
        self.log('Auto off is ' + str(self.sleepTimeValue))
        self.infoOnChange = REAL_SETTINGS.getSetting("InfoOnChange") == "true"
        self.log('Show info label on channel change is ' + str(self.infoOnChange))
        self.showChannelBug = REAL_SETTINGS.getSetting("ShowChannelBug") == "true"
        self.log('Show channel bug - ' + str(self.showChannelBug))
        self.forceReset = REAL_SETTINGS.getSetting('ForceChannelReset') == "true"
        self.channelResetSetting = REAL_SETTINGS.getSetting('ChannelResetSetting')
        self.log("Channel reset setting - " + str(self.channelResetSetting))
        self.channelLogos = xbmc.translatePath(REAL_SETTINGS.getSetting('ChannelLogoFolder'))
        self.backgroundUpdating = int(REAL_SETTINGS.getSetting("ThreadMode"))
        self.log("Background updating - " + str(self.backgroundUpdating))
        self.showNextItem = REAL_SETTINGS.getSetting("EnableComingUp") == "true"
        self.log("Show Next Item - " + str(self.showNextItem))
        self.hideShortItems = REAL_SETTINGS.getSetting("HideClips") == "true"
        self.log("Hide Short Items - " + str(self.hideShortItems))
        self.shortItemLength = SHORT_CLIP_ENUM[int(REAL_SETTINGS.getSetting("ClipLength"))]
        self.log("Short item length - " + str(self.shortItemLength))

        if FileAccess.exists(self.channelLogos) == False:
            self.channelLogos = IMAGES_LOC

        self.log('Channel logo folder - ' + self.channelLogos)
        chn = ChannelList()
        chn.myOverlay = self
        self.channels = chn.setupList()

        if self.channels is None:
            self.log('readConfig No channel list returned')
            self.end()
            return False

        self.Player.stop()
        self.log('readConfig return')
        return True


    # handle fatal errors: log it, show the dialog, and exit
    def Error(self, line1, line2 = '', line3 = ''):
        self.log('FATAL ERROR: ' + line1 + " " + line2 + " " + line3, xbmc.LOGFATAL)
        dlg = xbmcgui.Dialog()
        dlg.ok('Error', line1, line2, line3)
        del dlg
        self.end()
        return


    def channelDown(self):
        self.log('channelDown')

        if self.maxChannels == 1:
            return

        self.background.setVisible(True)
        channel = self.fixChannel(self.currentChannel - 1, False)
        self.setChannel(channel)
        self.background.setVisible(False)
        self.log('channelDown return')


    def channelUp(self):
        self.log('channelUp')

        if self.maxChannels == 1:
            return

        self.background.setVisible(True)
        channel = self.fixChannel(self.currentChannel + 1)
        self.setChannel(channel)
        self.background.setVisible(False)
        self.log('channelUp return')


    def message(self, data):
        self.log('Dialog message: ' + data)
        dlg = xbmcgui.Dialog()
        dlg.ok('Info', data)
        del dlg


    def log(self, msg, level = xbmc.LOGERROR):
        log('TVOverlay: ' + msg, level)


    # set the channel, the proper show offset, and time offset
    def setChannel(self, channel):
        self.log('setChannel ' + str(channel))
        
        if self.Player.stopped:
            self.log('setChannel player already stopped', xbmc.LOGERROR);
            return

        self.lastActionTime = 0
        timedif = 0
        self.getControl(102).setVisible(False)
        self.getControl(103).setImage('')
        self.showingInfo = False

        # first of all, save playing state, time, and playlist offset for
        # the currently playing channel
   
	self.currentChannel = channel
        # now load the proper channel playlist
        xbmc.PlayList(xbmc.PLAYLIST_MUSIC).clear()
        self.log("about to load");

        if xbmc.PlayList(xbmc.PLAYLIST_MUSIC).load(PLAYLIST_PATH + str(channel) + '.m3u') == False:
            self.log("Error loading playlist", xbmc.LOGERROR)
            self.InvalidateChannel(channel)
            return
	if xbmc.PlayList(xbmc.PLAYLIST_MUSIC).size()==0:
	    self.Error('nothing found')
	    return
		

        # Disable auto playlist shuffling if it's on
        if xbmc.getInfoLabel('Playlist.Random').lower() == 'random':
            self.log('Random on.  Disabling.')
	    xbmc.PlayList(xbmc.PLAYLIST_MUSIC).unshuffle()
	xbmc.PlayList(xbmc.PLAYLIST_MUSIC).shuffle()
        self.log("repeat all");
        xbmc.executebuiltin("PlayerControl(repeatall)")
        curtime = time.time()
        self.log("about to mute");
        # Mute the channel before changing
        xbmc.executebuiltin("Mute()");
        # set the show offset
        self.Player.playselected(int(self.currentIdx))
        self.log("playing selected file");
        # set the time offset
        # Unmute
        self.log("Finished, unmuting");
        xbmc.executebuiltin("Mute()");
        self.lastActionTime = time.time()
        self.log('setChannel return')


    def InvalidateChannel(self, channel):
        self.log("InvalidateChannel" + str(channel))

        if channel < 1 or channel > self.maxChannels:
            self.log("InvalidateChannel invalid channel " + str(channel))
            return

        self.channels[channel - 1].isValid = False
        self.invalidatedChannelCount += 1

        if self.invalidatedChannelCount > 3:
            self.Error("Exceeded 3 invalidated channels. Exiting.")
            return

        remaining = 0

        for i in range(self.maxChannels):
            if self.channels[i].isValid:
                remaining += 1

        if remaining == 0:
            self.Error("No channels available. Exiting.")
            return

        self.setChannel(self.fixChannel(channel))


    def waitForVideoPaused(self):
        self.log('waitForVideoPaused')
        sleeptime = 0

        while sleeptime < TIMEOUT:
            xbmc.sleep(100)

            if self.Player.isPlaying():
                if xbmc.getCondVisibility('Player.Paused'):
                    break

            sleeptime += 100
        else:
            self.log('Timeout waiting for pause', xbmc.LOGERROR)
            return False

        self.log('waitForVideoPaused return')
        return True


    def setShowInfo(self):
        self.log('setShowInfo')

        if self.infoOffset > 0:
            self.getControl(502).setLabel('COMING UP:')
        elif self.infoOffset < 0:
            self.getControl(502).setLabel('ALREADY SEEN:')
        elif self.infoOffset == 0:
            self.getControl(502).setLabel('NOW WATCHING:')

        position = xbmc.PlayList(xbmc.PLAYLIST_MUSIC).getposition() + self.infoOffset
        
        item = self.getListItem(position)

        self.getControl(503).setLabel(item['title'])
        self.getControl(504).setLabel(item['rating'])
        self.getControl(505).setLabel(item['description'])
        self.getControl(506).setImage(item['poster'])
        self.log('setShowInfo return')

    def getListItem(self,position):
        item = {}
        try:
            playlistitem= xbmc.PlayListItem()
            playlistitem = xbmc.PlayList(xbmc.PLAYLIST_MUSIC).__getitem__(position)
            
            description = playlistitem.getdescription()
            myarray = description.split('//')
            item['title'] = myarray[0]
            try:
                item['rating'] = myarray[1]
            except:
                item['rating'] = ''
            item['poster'] = 'http://'+ myarray[2]
            item['imdbid'] = myarray[3]
            item['description'] = myarray[4]    
        except:
            item['title'] = 'unsupported'
            item['rating'] = ''
            item['poster'] = ''
            item['imdbid'] = ''
            item['description'] = ''
            self.end()
            return
            
        return item



    def hideInfo(self):
        self.getControl(102).setVisible(False)
        self.infoOffset = 0
        self.showingInfo = False

        if self.infoTimer.isAlive():
            self.infoTimer.cancel()

        self.infoTimer = threading.Timer(5.0, self.hideInfo)


    def showInfo(self, timer):
        self.getControl(102).setVisible(True)
        self.showingInfo = True
        self.setShowInfo()

        if self.infoTimer.isAlive():
            self.infoTimer.cancel()

        self.infoTimer = threading.Timer(timer, self.hideInfo)
        self.infoTimer.name = "InfoTimer"

        if xbmc.getCondVisibility('Player.ShowInfo'):
            xbmc.executehttpapi("SendKey(0xF049)")
            self.ignoreInfoAction = True

        self.infoTimer.start()


    # return a valid channel in the proper range
    def fixChannel(self, channel, increasing = True):
        while channel < 1 or channel > self.maxChannels:
            if channel < 1: channel = self.maxChannels + channel
            if channel > self.maxChannels: channel -= self.maxChannels

        if increasing:
            direction = 1
        else:
            direction = -1

        if self.channels[channel - 1].isValid == False:
            return self.fixChannel(channel + direction, increasing)

        return channel


    # Handle all input while videos are playing
    def onAction(self, act):
        action = act.getId()
        self.log('onAction ' + str(action))

        if self.Player.stopped:
            return

        # Since onAction isnt always called from the same thread (weird),
        # ignore all actions if we're in the middle of processing one
        if self.actionSemaphore.acquire(False) == False:
            self.log('Unable to get semaphore')
            return

        lastaction = time.time() - self.lastActionTime

        # during certain times we just want to discard all input
        if lastaction < 2:
            self.log('Not allowing actions')
            action = ACTION_INVALID

        self.startSleepTimer()
        
        if action == ACTION_SELECT_ITEM:
            if self.showingInfo and self.infoOffset<>0:       
                try:
                    position = xbmc.PlayList(xbmc.PLAYLIST_MUSIC).getposition() + self.infoOffset
                except:
                    position = 0
            if self.showingInfo:
                self.hideInfo()
                try:
                    self.Player.playselected(position)
                except:
                    pass
            else:
                self.Player.pause()
                position = xbmc.PlayList(xbmc.PLAYLIST_MUSIC).getposition()
                item = self.getListItem(position)
                imdbid = item['imdbid']
                type = item['rating']
            if 'Watchlist' in type:
				mytext='Remove From Watchlist'
				myaction='trakt_RemoveMoviefromWatchlist'
            else:
				mytext='Add to Watchlist'
				myaction='trakt_AddMovietoWatchlist'
            
            dlg = xbmcgui.Dialog()
            ret = dlg.select('What you want to do?', ['Watch Now', 'Mark as seen', mytext, 'Dismiss' , 'Cancel'])
            if ret==0:
				action ='SearchMe'
            elif ret==1:
				action = 'trakt_SeenRate'
            elif ret==2:
				action = myaction
            elif ret==3:
				action = 'trakt_DismissMovie'
            else:
				action = 'exit'
            if action != 'exit' :
                xbmc.executebuiltin("XBMC.RunScript(special://home/addons/plugin.video.furklibraryx/default.py,0,?action="+action+"&type=Movie&go=Now&imdbid=" + imdbid +")")
                if action == 'SearchMe':
					self.end()
					return  # Don't release the semaphore
                self.startSleepTimer()
                self.Player.pause()
            else:
                self.startSleepTimer()
                self.Player.pause()
        elif action == ACTION_MOVE_UP or action == ACTION_PAGEUP:
            #self.channelUp()
            self.Player.playnext()
        elif action == ACTION_MOVE_DOWN or action == ACTION_PAGEDOWN:
            #self.channelDown()
	    self.Player.playprevious()
        elif action == ACTION_MOVE_LEFT:
                self.infoOffset -= 1
                self.showInfo(10.0)
        elif action == ACTION_MOVE_RIGHT:
	        self.infoOffset += 1
                self.showInfo(10.0)
        elif action in ACTION_PREVIOUS_MENU:
            if self.showingInfo:
                self.hideInfo()
            else:
                dlg = xbmcgui.Dialog()

                if self.sleepTimeValue > 0:
                    if self.sleepTimer.isAlive():
                        self.sleepTimer.cancel()
                        self.sleepTimer = threading.Timer(self.sleepTimeValue, self.sleepAction)

                if dlg.yesno("Exit?", "Are you sure you want to exit Furk Trailers?"):
                    self.end()
                    return  # Don't release the semaphore
                else:
                    self.startSleepTimer()

                del dlg
        elif action == ACTION_SHOW_INFO:
            if self.ignoreInfoAction:
                self.ignoreInfoAction = False
            else:
                if self.showingInfo:
                    self.hideInfo()

                    if xbmc.getCondVisibility('Player.ShowInfo'):
                        xbmc.executehttpapi("SendKey(0xF049)")
                        self.ignoreInfoAction = True
                else:
                    self.showInfo(10.0)

        elif action == ACTION_OSD:
            xbmc.executebuiltin("ActivateWindow(12901)")

        self.actionSemaphore.release()
        self.log('onAction return')


    # Reset the sleep timer
    def startSleepTimer(self):
        if self.sleepTimeValue == 0:
            return

        # Cancel the timer if it is still running
        if self.sleepTimer.isAlive():
            self.sleepTimer.cancel()
            self.sleepTimer = threading.Timer(self.sleepTimeValue, self.sleepAction)

        if self.Player.stopped == False:
            self.sleepTimer.name = "SleepTimer"
            self.sleepTimer.start()


    def startNotificationTimer(self, timertime = NOTIFICATION_CHECK_TIME):
        self.log("startNotificationTimer")

        if self.notificationTimer.isAlive():
            self.notificationTimer.cancel()

        self.notificationTimer = threading.Timer(timertime, self.notificationAction)

        if self.Player.stopped == False:
            self.notificationTimer.name = "NotificationTimer"
            self.notificationTimer.start()


    # This is called when the sleep timer expires
    def sleepAction(self):
        self.log("sleepAction")
        self.actionSemaphore.acquire()
#        self.sleepTimer = threading.Timer(self.sleepTimeValue, self.sleepAction)
        # TODO: show some dialog, allow the user to cancel the sleep
        # perhaps modify the sleep time based on the current show
        self.end()
        return


    # Run rules for a channel
    def runActions(self, action, channel, parameter):
        self.log("runActions " + str(action) + " on channel " + str(channel))

        if channel < 1:
            return

        self.runningActionChannel = channel
        index = 0

        for rule in self.channels[channel - 1].ruleList:
            if rule.actions & action > 0:
                self.runningActionId = index
                parameter = rule.runAction(action, self, parameter)

            index += 1

        self.runningActionChannel = 0
        self.runningActionId = 0
        return parameter


    def notificationAction(self):
        self.log("notificationAction")
        docheck = False

        if self.Player.isPlaying():
	    if self.Player.getTime()<5:
		    print 'time:' + str(self.Player.getTime())
	            if not self.showingInfo:
			self.infoOffset = 0
	                self.showInfo(5.0)
		    settings.setSetting('last_trailer',str(xbmc.PlayList(xbmc.PLAYLIST_MUSIC).getposition()))
		


            if self.notificationLastChannel != self.currentChannel:
                docheck = True
            else:
                if self.notificationLastShow != xbmc.PlayList(xbmc.PLAYLIST_MUSIC).getposition():
                    docheck = True
                else:
                    if self.notificationShowedNotif == False:
                        docheck = True

            if docheck == True:
                self.notificationLastChannel = self.currentChannel
                self.notificationLastShow = xbmc.PlayList(xbmc.PLAYLIST_MUSIC).getposition()
                self.notificationShowedNotif = False

                timedif = self.Player.getTotalTime() - self.Player.getTime()

                if self.notificationShowedNotif == False and timedif < NOTIFICATION_TIME_BEFORE_END and timedif > NOTIFICATION_DISPLAY_TIME:
                    nextshow = self.notificationLastShow + 1
		    item = self.getListItem(nextshow)

		    title = item['title']
		    xbmc.executebuiltin("Notification(Coming Up Next, " + title.replace(',', '') + ", " + str(NOTIFICATION_DISPLAY_TIME * 1000) + ")")
		    if not self.showingInfo:
			self.infoOffset = 0
	                self.showInfo(5.0)
                    self.notificationShowedNotif = True

        self.startNotificationTimer()


    def playerTimerAction(self):
        self.playerTimer = threading.Timer(2.0, self.playerTimerAction)

        if self.Player.isPlaying():
            self.lastPlayTime = int(self.Player.getTime())
            self.lastPlaylistPosition = xbmc.PlayList(xbmc.PLAYLIST_MUSIC).getposition()
            self.notPlayingCount = 0
        else:
            self.notPlayingCount += 1
            self.log("Adding to notPlayingCount")

        if self.Player.stopped == False:
            self.playerTimer.name = "PlayerTimer"
            self.playerTimer.start()


    # cleanup and end
    def end(self):
        self.log('end')
        # Prevent the player from setting the sleep timer
        self.Player.stopped = True
        self.background.setVisible(True)
        curtime = time.time()
        xbmc.executebuiltin("PlayerControl(repeatoff)")
        self.isExiting = True
        

        if self.playerTimer.isAlive():
            self.playerTimer.cancel()
            self.playerTimer.join()

        if self.Player.isPlaying():
            self.lastPlayTime = self.Player.getTime()
            self.lastPlaylistPosition = xbmc.PlayList(xbmc.PLAYLIST_MUSIC).getposition()
            self.Player.stop()

        

        try:
            if self.channelLabelTimer.isAlive():
                self.channelLabelTimer.cancel()
                self.channelLabelTimer.join()
        except:
            pass

        

        try:
            if self.notificationTimer.isAlive():
                self.notificationTimer.cancel()
                self.notificationTimer.join()
        except:
            pass

        
        try:
            if self.infoTimer.isAlive():
                self.infoTimer.cancel()
                self.infoTimer.join()
        except:
            pass

        

        try:
            if self.sleepTimeValue > 0:
                if self.sleepTimer.isAlive():
                    self.sleepTimer.cancel()
        except:
            pass

        


        self.background.setVisible(False)
        self.close()
