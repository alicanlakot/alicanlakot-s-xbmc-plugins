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

import time
from utils import settings
print "[PLUGIN] Furk Lib Service initialized!" 

time.sleep(60)
XBMC.RunScript("special://home/addons/plugin.video.furklibraryx/default.py,0,?action=traktlib&fg=False")
settings.startTimer()