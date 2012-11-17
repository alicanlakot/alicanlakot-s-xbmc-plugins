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
import inspect
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


    


# overlay window to catch events and change channels
class TVOverlay(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
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


    

    def onFocus(self, controlId):
        pass


    def onInit(self):
        self.background = self.getControl(101)
        self.getControl(102).setVisible(False)
        self.background.setVisible(True)
        self.currentIdx=settings.getSetting('last_trailer')
        if self.currentIdx == '':
            self.currentIdx = 0
        

        self.playerTimer = threading.Timer(2.0, self.playerTimerAction)
        self.playerTimer.name = "PlayerTimer"
        self.infoTimer = threading.Timer(5.0, self.hideInfo)
        # self.myEPG = EPGWindow("script.FurkTrailers.EPG.xml", ADDON_INFO, "default")
        # self.myEPG.MyOverlayWindow = self
        # Don't allow any actions during initialization
        self.actionSemaphore.acquire()
        
    
    # Akin
        refresh = createTrailers.getReco(1)
        if refresh:
            self.currentIdx = 0
        
        self.timeStarted = time.time()
        self.notificationTimer = threading.Timer(5, self.notificationAction)
        self.currentChannel = 1
        self.setChannel(self.currentChannel)
        self.background.setVisible(False)
        self.startNotificationTimer()
        self.playerTimer.start()



        self.actionSemaphore.release()
        self.log('onInit return')

        
    def log(self, msg, level = xbmc.LOGERROR):
        log('TVOverlay: ' + msg, level)


    # setup all basic configuration parameters, including creating the playlists that
    # will be used to actually run this thing
   

    # set the channel, the proper show offset, and time offset
    def setChannel(self, channel):
        
        self.lastActionTime = 0
        timedif = 0
        self.getControl(102).setVisible(False)
        self.getControl(103).setImage('')
        self.showingInfo = False
        self.currentChannel = channel
        
        
        with open(PLAYLIST_PATH + str(channel) + '.m3u') as f:
            self.content = f.readlines()
        
        
        myPl = PLAYLIST_PATH + str(channel) + '.m3u'
        #xbmc.executebuiltin('PlayMedia(' + content[1] + ')')        
        self.Player.play(myPl)
        #xbmc.PlayList(1).load(myPl)
        #xbmc.Player.play()

  
  
    def setShowInfo(self):
        
        position = xbmc.PlayList(xbmc.PLAYLIST_VIDEO).getposition() + self.infoOffset
        if position < 0 :
            position = 0
            self.infoOffset = 0

        if self.infoOffset > 0:
            self.getControl(502).setLabel('COMING UP:')
        elif self.infoOffset < 0:
            self.getControl(502).setLabel('ALREADY SEEN:')
        elif self.infoOffset == 0:
            self.getControl(502).setLabel('NOW WATCHING:')
            
        
        position = xbmc.PlayList(xbmc.PLAYLIST_VIDEO).getposition() + self.infoOffset
        print 'Akin' + str(position)
        
        item = self.getListItem(position)
        
        print item

        self.getControl(503).setLabel(item['title'])
        self.getControl(504).setLabel(item['rating'])
        self.getControl(505).setLabel(item['description'])
        self.getControl(506).setImage(item['poster'])
        

    def getListItem(self,position):
                item = {}
        
            
                #playlistitem = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)[position]
                indx= 2*position+1
                print indx
                description = self.content[indx][11:]
                #print description
                #description = playlistitem.getdescription()
                myarray = description.split('//')
                item['title'] = myarray[0]
                try:
                    item['rating'] = myarray[1]
                except:
                    item['rating'] = ''
                item['poster'] = 'http://'+ myarray[2]
                item['imdbid'] = myarray[3]
                item['description'] = myarray[4]    
#            except:
#                item['title'] = 'undefined'
#                item['rating'] = ''
#                item['poster'] = ''
#                item['imdbid'] = '0'
#                item['description'] =''
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
            xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Input.Info","id":1}')
            self.ignoreInfoAction = True

        self.infoTimer.start()


    

    # Handle all input while videos are playing
    
    def onAction(self, act):
        action = act.getId()
        

        if self.Player.stopped:
            return

        # Since onAction isnt always called from the same thread (weird),
        # ignore all actions if we're in the middle of processing one
        
        lastaction = time.time() - self.lastActionTime

        # during certain times we just want to discard all input
        if lastaction < 2:
            action = ACTION_INVALID

        
        
        if action == ACTION_SELECT_ITEM:
            if self.showingInfo and self.infoOffset<>0:
                position = xbmc.PlayList(xbmc.PLAYLIST_VIDEO).getposition() + self.infoOffset
                item = self.getListItem(position)
                print 'pos:' + str(position) + 'title:' + item['title']
                self.hideInfo()
                self.Player.playselected(position)

            else:
                self.Player.pause()
                position = xbmc.PlayList(xbmc.PLAYLIST_MUSIC).getposition()
                item = self.getListItem(position)
                imdbid = item['imdbid']
                myType = item['rating']
                if 'Watchlist' in myType:
                    mytext = 'Remove From Watchlist'
                    myaction = 'trakt_RemoveMoviefromWatchlist'
                else:
                    mytext = 'Add to Watchlist'
                    myaction = 'trakt_AddMovietoWatchlist'
            
                dlg = xbmcgui.Dialog()
                ret = dlg.select('What you want to do?', ['Watch Now', 'Mark as seen', mytext, 'Dismiss' , 'Cancel'])
                if ret == 0:
                    action = 'SearchMe'
                elif ret == 1:
                    action = 'trakt_SeenRate'
                elif ret == 2:
                    action = myaction
                elif ret == 3:
                    action = 'trakt_DismissMovie'
                else:
                    action = 'exit'
                    
                    
                if action != 'exit' :
                    xbmc.executebuiltin("XBMC.RunScript(special://home/addons/plugin.video.furklibraryx/default.py,0,?action=" + action + "&type=Movie&go=Now&imdbid=" + imdbid + ")")
                    if action == 'SearchMe':
                        self.Player.stop()
                        self.end()
                        return  # Don't release the semaphore
                
                    self.Player.pause()
                else:
                    self.Player.pause()
                    
        elif action == ACTION_MOVE_UP or action == ACTION_PAGEUP:
            # self.channelUp()
            self.Player.playnext()
        elif action == ACTION_MOVE_DOWN or action == ACTION_PAGEDOWN:
            # self.channelDown()
            self.Player.playprevious()
        elif action == ACTION_MOVE_LEFT:
            self.infoOffset -= 1
            self.showInfo(10.0)
        elif action == ACTION_MOVE_RIGHT:
            self.infoOffset += 1
            self.showInfo(10.0)
        elif action == ACTION_STOP:
            self.end()
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
                    self.Player.stop()
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
                        xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Input.Info","id":1}')
                        self.ignoreInfoAction = True
                else:
                    self.showInfo(10.0)

        elif action == ACTION_OSD:
            xbmc.executebuiltin("ActivateWindow(12901)")

        
        


        


    # Run rules for a channel
    def runActions(self, action, channel, parameter):
        

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
        
        docheck = False

        if self.Player.isPlaying():
            if self.Player.getTime() < 5:
                print 'time:' + str(self.Player.getTime())
                if not self.showingInfo:
                    self.infoOffset = 0
                    self.showInfo(5.0)
                    settings.setSetting('last_trailer', str(xbmc.PlayList(xbmc.PLAYLIST_MUSIC).getposition()))


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
            if self.notPlayingCount > 5:
                self.end()
            

        if self.Player.stopped == False:
            self.playerTimer.name = "PlayerTimer"
            self.playerTimer.start()

    def startNotificationTimer(self, timertime = NOTIFICATION_CHECK_TIME):
        self.log("startNotificationTimer")

        if self.notificationTimer.isAlive():
            self.notificationTimer.cancel()

        self.notificationTimer = threading.Timer(timertime, self.notificationAction)

        if self.Player.stopped == False:
            self.notificationTimer.name = "NotificationTimer"
            self.notificationTimer.start()


    # cleanup and end
    def end(self):
        
        # Prevent the player from setting the sleep timer
        self.Player.stopped = True
        self.background.setVisible(True)
        xbmc.executebuiltin("PlayerControl(repeatoff)")
        self.isExiting = True
        self.background.setVisible(False)
        self.close()
