import argparse

import torch

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
		self.imageFolder = "/home/nil/Nil/My Codes/Projects/annotation tool/fbrs_interactive_segmentation/images/"
		self.images = self.get_files(self.imageFolder,address=True,exts=[".jpg"])

		self.weightsPath = "/home/nil/Nil/My Codes/Projects/annotation tool/fbrs_interactive_segmentation/weights/resnet34_dh128_sbd.pth"
		self.makeModel()

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
		# args, cfg = parse_args()
		# print(args)
		# print(cfg)

		# torch.backends.cudnn.deterministic = True
		# checkpoint_path = utils.find_checkpoint(cfg.INTERACTIVE_MODELS_PATH, args.checkpoint)
		# model = utils.load_is_model(checkpoint_path, args.device, cpu_dist_maps=True, norm_radius=args.norm_radius)

		# self.passArgs = arg
		# self.model = model

		ScreenMan = ScreenManagerbuild()
		# ScreenMan.add_widget(mainScreen(name='fgHome',args=passArgs,model=self.model))
		ScreenMan.add_widget(mainScreen(name='fgHome',arg="xxx"))

		return ScreenMan

class ScreenManagerbuild(ScreenManager):
	pass

print("name")
if __name__ == '__main__':
	print("correct")
	MainClass().run()
