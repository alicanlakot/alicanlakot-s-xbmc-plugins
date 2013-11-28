#   Copyright (C) 2011 Jason Anderson
#
#
# This file is part of PseudoTV.
#
# PseudoTV is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PseudoTV is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PseudoTV.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os, threading
import xbmc, xbmcgui
import xbmcaddon

from resources.lib.Globals import *



# Script constants
__scriptname__ = "Furk Trailers"
__author__     = "Alicanlakot"
__url__        = "http://github.com/alicanlakot"
__version__    = '1.2.0'
__settings__   = xbmcaddon.Addon(id='plugin.video.furklibraryx')
__language__   = __settings__.getLocalizedString
__cwd__        = __settings__.getAddonInfo('path')
PLAYLIST_PATH = os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.furklibraryx/'), '')
CACHE_PATH= os.path.join(xbmc.translatePath('special://profile/addon_data/plugin.video.furklibraryx/traktcache'), '')
MOVIES_PATH ='not used'
TV_SHOWS_PATH='not used'

import resources.lib.Overlay as Overlay


MyOverlayWindow = Overlay.TVOverlay("script.pseudotv.TVOverlay.xml", __cwd__, "default")

del MyOverlayWindow
xbmcgui.Window(10000).setProperty("FurkTrailersRunning", "False")

