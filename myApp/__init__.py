from .importer import *
from .viewInfo import viewInfo
from .viewScreen import viewScreen
from .toolFunctions import toolFunctions

class myApp(viewInfo,viewScreen,toolFunctions):
	def __init__(self):
		viewInfo.__init__(self)
		viewScreen.__init__(self)
		toolFunctions.__init__(self)
		print("init myApp")

	def getRoll(self,size_hint,pos_hint,grid,direction="ver"):
		gScroll = ScrollView(size_hint=size_hint,pos_hint=pos_hint, size=(grid.width, grid.height))
		if direction=="hor":
			gRoll = GridLayout(cols=0,spacing=3, size_hint_x=None,padding=5)
			gRoll.bind(minimum_width=gRoll.setter('width'))
		elif direction=="ver":
			gRoll = GridLayout(cols=1,spacing=3, size_hint_y=None,padding=5)
			gRoll.bind(minimum_height=gRoll.setter('height'))
		elif direction=="both":
			gRoll = GridLayout(cols=1, size_hint_y=None, size_hint_x=None, spacing=2, padding=2)
			gRoll.bind(minimum_height=gRoll.setter('height'))
			gRoll.bind(minimum_width=gRoll.setter('width'))
		gScroll.add_widget(gRoll)
		grid.add_widget(gScroll)

		return gScroll, gRoll
