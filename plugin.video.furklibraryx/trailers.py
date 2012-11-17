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


import xbmc, xbmcgui
import xbmcaddon


# Script constants
__scriptname__ = "Furk Trailers"
__author__     = "alicanlakot"
__url__        = "http://github.com/alicanlakot"
__settings__   = xbmcaddon.Addon(id='plugin.video.furklibraryx')
__cwd__        = __settings__.getAddonInfo('path')


xbmc.executebuiltin('RunScript("' + __cwd__ + '/trailersctrl.py' + '")')
