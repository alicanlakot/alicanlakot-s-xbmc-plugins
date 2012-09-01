import xbmcgui

class context:
	'''
	Hack to get current context that addon is running in
	@usage context = context().getContext()
	@author chippyash
	@thanks amet - xbmc.org
	@link http://wiki.xbmc.org/index.php?title=Window_IDs
	'''
	# Set up window Ids for the various contexts
	_ctxt_audio = (10005,10500,10501,10502)
	_ctxt_video = (10006,10024,10025,10028)
	_ctxt_image = (10002)
	_ctxt_executable = (10001,10020)
	# current window id
	_currId = 0;
	
	def __init__(self):
		self._currId = xbmcgui.getCurrentWindowId();

	def getContext(self):
		'''
		Returns the current system context
		@return string	('audio','video','image','executable','unknown')
		'''
		if self._currId in self._ctxt_audio:
			return 'audio'
		elif self._currId in self._ctxt_video:
			return 'video'
		elif self._currId in self._ctxt_image:
			return 'image'
		elif self._currId in self._ctxt_executable:
			return 'executable'
		else:
			return 'unknown'

