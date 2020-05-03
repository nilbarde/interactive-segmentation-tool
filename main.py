from myApp import *
from myModel import myModel

class mainScreen(Screen,myApp,myModel):
	def __init__(self,**kwargs):
		Screen.__init__(self)
		myApp.__init__(self)
		myModel.__init__(self)
		self.startTool()

	def startTool(self):
		self.imageNow = 0
		self.imageFolder = "/home/nil/Nil/My Codes/Projects/annotation tool/images/"
		self.images = self.get_files(self.imageFolder,address=True,exts=None)

		self.weightsPath = "/home/nil/model/weights.csv"

		self.loadScreen()
		self.imageLoad(self.imageNow)

	def on_touch_down(self,touch):
		super(mainScreen, self).on_touch_down(touch)
		self.clickInCanvas(touch)

	def doNothing(self,*args):
		print(args)
		print("awesomes")

class MainClass(App):
	def build(self):
		ScreenMan = ScreenManagerbuild()
		ScreenMan.add_widget(mainScreen(name='fgHome'))

		return ScreenMan

class ScreenManagerbuild(ScreenManager):
	pass

if __name__ == '__main__':
	MainClass().run()
