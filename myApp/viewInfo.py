from functools import partial

class viewInfo:
	def __init__(self):
		print("init viewInfo")

	def setDimensions(self,*args):
		# center_x is center of widget in horizontal direction
		# center_y is center of widget in vertical direction
		# dimension is along horizontal, vertical direction

		self.imgPos = {"center_x":0.3,"center_y":0.55} 
		self.imgDim = (0.6,0.6)
		self.imgRatioWidth = 1.0
		self.imgRatioHeight = 1.0

		self.imgHeight = 1000
		self.imgWidth = 1750
		self.setCanvasDim()

		self.inputs = {}

		x = "model-weights path"
		self.inputs[x] = {}
		self.inputs[x]["pos"] = {"center_x":0.5,"center_y":0.97}
		self.inputs[x]["dim"] = (0.9,0.055)
		self.inputs[x]["fun"] = self.modelLoad
		self.inputs[x]["val"] = self.weightsPath

		x = "image folder path"
		self.inputs[x] = {}
		self.inputs[x]["pos"] = {"center_x":0.5,"center_y":0.91}
		self.inputs[x]["dim"] = (0.9,0.055)
		self.inputs[x]["fun"] = self.doNothing
		self.inputs[x]["val"] = self.imageFolder

		self.btns = {}

		x = "+"
		self.btns[x] = {}
		self.btns[x]["pos"] = {"center_x":0.4,"center_y":0.15}
		self.btns[x]["dim"] = (0.09,0.08)
		self.btns[x]["fun"] = partial(self.zoomDir,x)

		x = "|"
		self.btns[x] = {}
		self.btns[x]["pos"] = {"center_x":0.3,"center_y":0.15}
		self.btns[x]["dim"] = (0.09,0.08)
		self.btns[x]["fun"] = partial(self.zoomDir,x)

		x = "-"
		self.btns[x] = {}
		self.btns[x]["pos"] = {"center_x":0.2,"center_y":0.15}
		self.btns[x]["dim"] = (0.09,0.08)
		self.btns[x]["fun"] = partial(self.zoomDir,x)

		x = "next"
		self.btns[x] = {}
		self.btns[x]["pos"] = {"center_x":0.66,"center_y":0.80}
		self.btns[x]["dim"] = (0.10,0.06)
		self.btns[x]["fun"] = self.imageNext

		x = "undo"
		self.btns[x] = {}
		self.btns[x]["pos"] = {"center_x":0.78,"center_y":0.80}
		self.btns[x]["dim"] = (0.10,0.06)
		self.btns[x]["fun"] = self.imageUndo

		x = "reset"
		self.btns[x] = {}
		self.btns[x]["pos"] = {"center_x":0.90,"center_y":0.80}
		self.btns[x]["dim"] = (0.10,0.06)
		self.btns[x]["fun"] = self.imageReset

		self.stages = {}
		self.stagesGridPos = {"center_x":0.78,"center_y":0.55}
		self.stagesGridDim = (0.36,0.35)
		self.stageNow = 2

		x = 1
		self.stages[x] = {}
		self.stages[x]["task"] = "add/remove nuclei"
		self.stages[x]["fun"] = partial(self.stageSwitch,x)
		self.stages[x][True] = partial(self.nucleiAdd)
		self.stages[x][False] = partial(self.nucleiRemove)

		x = 2
		self.stages[x] = {}
		self.stages[x]["task"] = "improve detected"
		self.stages[x]["fun"] = partial(self.stageSwitch,x)
		self.stages[x][True] = partial(self.nucleiPartAdd)
		self.stages[x][False] = partial(self.nucleiPartRemove)

		self.sliders = {}
		self.sliderGridPos = {"center_x":0.78,"center_y":0.25}
		self.sliderGridDim = (0.36,0.45)

		x = "zoom percent"
		self.sliders[x] = {}
		self.sliders[x]["min"] = 0
		self.sliders[x]["max"] = 200
		self.sliders[x]["val"] = 40
		self.sliders[x]["step"] = 1
		self.sliders[x]["fun"] = partial(self.updateSlider,x)

		x = "prediction threshold"
		self.sliders[x] = {}
		self.sliders[x]["min"] = 0
		self.sliders[x]["max"] = 1
		self.sliders[x]["val"] = 0.5
		self.sliders[x]["step"] = 0.01
		self.sliders[x]["fun"] = partial(self.updateSlider,x)

		x = "overlay alpha"
		self.sliders[x] = {}
		self.sliders[x]["min"] = 0
		self.sliders[x]["max"] = 1
		self.sliders[x]["val"] = 0.5
		self.sliders[x]["step"] = 0.01
		self.sliders[x]["fun"] = partial(self.updateSlider,x)

		x = "click radius"
		self.sliders[x] = {}
		self.sliders[x]["min"] = 5
		self.sliders[x]["max"] = 25
		self.sliders[x]["val"] = 10
		self.sliders[x]["step"] = 1
		self.sliders[x]["fun"] = partial(self.updateSlider,x)

	def setCanvasDim(self):
		self.canvasXmin = self.imgPos["center_x"] - self.imgDim[0]/2
		self.canvasXmax = self.canvasXmin + self.imgDim[0]*self.imgRatioWidth

		self.canvasYmax = self.imgPos["center_y"] + self.imgDim[1]/2
		self.canvasYmin = self.canvasYmax - self.imgDim[1]*self.imgRatioHeight
		print(self.canvasXmin,self.canvasXmax,self.canvasYmin,self.canvasYmax)
