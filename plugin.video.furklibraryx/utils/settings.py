DEBUG = False
try:
    import xbmcaddon,xbmc
    ADDON = xbmcaddon.Addon(id='plugin.video.furklibraryx')
except:
    ADDON = None

def getSetting(myKey):
    if ADDON:
        return ADDON.getSetting(myKey)
    else:
        if myKey=='trakt_login':
            return 'akina'
        elif myKey=='trakt_password':
            return '*****'
        else:
            return ADDON.getSetting(myKey)
def setSetting(myKey,myValue):
	ADDON.setSetting(id=myKey,value=myValue)
def openSettings():
	ADDON.openSettings()
def getTimersetting():
	timer_amounts = {}
	timer_amounts['0'] = '60'
	timer_amounts['1'] = '120'
	timer_amounts['2'] = '300'
	timer_amounts['3'] = '600'
	timer_amounts['4'] = '900'
	timer_amounts['5'] = '1440'
	return timer_amounts[ADDON.getSetting("update_timer")]

def getQualitysetting():
	quality_amounts = {}
	quality_amounts['0'] = 0
	quality_amounts['1'] = 450
	quality_amounts['2'] = 750
	quality_amounts['3'] = 1200
	return quality_amounts[ADDON.getSetting("quality")],quality_amounts[ADDON.getSetting("quality")+1]

def startTimer():
	if ADDON.getSetting('auto_update') == "true":
		xbmc.executebuiltin("AlarmClock(updateFurklibrary,XBMC.RunScript(special://home/addons/plugin.video.furklibraryx/default.py,0,?action=traktlib&fg=False)," + getTimersetting() + ",True)")

def first_time_startup():
    if ADDON.getSetting('first_time_startup') == "false":
        return False
    else:
        return True
