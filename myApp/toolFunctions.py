from os import walk
from .importer import *
from torchvision import transforms

class toolFunctions():
	def __init__(self):
		print("init toolFunctions")

	def imageLoad(self,image_num=0,*args):
		print(image_num)
		if image_num >= len(self.images) or image_num < 0:
			return

		self.imageNow = image_num
		name = self.images[image_num]

		input_transform = transforms.Compose([
			transforms.ToTensor(),
			transforms.Normalize([.485, .456, .406], [.229, .224, .225])
		])

		self.image = cv2.cvtColor(cv2.imread(name), cv2.COLOR_BGR2RGB)
		self.image_nd = input_transform(self.image).to(self.device)
		self.predictor.set_input_image(self.image_nd)

		self.imgRoll.clear_widgets()
		self.imgGrid = FloatLayout(size_hint=(None,None),width=self.imgWidth,height=self.imgHeight)
		self.imgRoll.add_widget(self.imgGrid)

		self.imgGrid.canvas.clear()
		print(name)
		with self.imgGrid.canvas:
			self.img = Rectangle(source=name)
			self.imgWidth, self.imgHeight = (self.img.texture.size)
			self.imgGrid.width = self.imgWidth
			self.imgGrid.height = self.imgHeight
			Color(0,0,0,0)
			self.mask = Rectangle()
		self.imgGrid.bind(pos=partial(self._image_bind,self.imgGrid,self.img),size=partial(self._image_bind,self.imgGrid,self.img))

		self.sMaskGrid = FloatLayout(size_hint=self.maskDim,pos_hint=self.maskPos)
		self.add_widget(self.sMaskGrid)
		with self.sMaskGrid.canvas:
			Color(0,0,0,0)
			self.sMask = Rectangle()
		self.sMaskGrid.bind(pos=partial(self._image_bind,self.sMaskGrid,self.sMask),size=partial(self._image_bind,self.sMaskGrid,self.sMask))

		self.zoomNow = 1
		self.all_results = np.zeros((self.imgHeight, self.imgWidth),dtype="uint8")
		self.object_count = 0
		self.reset_predictor()
		# self.imgGrid.bind(pos=partial(self._image_bind,self.imgGrid,self.mask),size=partial(self._image_bind,self.imgGrid,self.mask))

	def imageNext(self,*args):
		self.imageLoad(self.imageNow+1)

	def imagePrev(self,*args):
		self.imageLoad(self.imageNow-1)

	def imageUndo(self,*args):
		self.undo_click()
		print("undo")
		self.image_saver()

	def imageReset(self,*args):
		self.imageLoad(self.imageNow)

	def modelLoad(self,*args):
		self.weightsPath = self.inputs["model-weights path"]["input"].text
		self.makeModel()
		self.imageLoad()

	# def nextObject(self,*args):

	def zoomDir(self,mode,x=None,y=None,*args):
		zoom = self.sliders["zoom percent"]["val"]
		if mode == "+":
			self.zoomNow *= (100+zoom)/100.0
		elif mode == "-":
			self.zoomNow /= (100+zoom)/100.0
		elif mode == "|":
			self.zoomNow = 1.0
		elif mode == "++":
			self.zoomNow *= (100+zoom/5)/100.0
		elif mode == "--":
			self.zoomNow /= (100+zoom/5)/100.0

		newWidth = self.imgWidth*self.zoomNow
		newHeight = self.imgHeight*self.zoomNow
		if type(x) is float and newWidth>self.imgScroll.width:
			point = (self.imgScroll.scroll_x*(self.imgRoll.width-self.imgScroll.width)+x*self.imgScroll.width)/(self.imgRoll.width)
			point *= newWidth
			point -= x*self.imgScroll.width
			point /= (newWidth - self.imgScroll.width)
			x = point
			x = min(1.0,x)
			x = max(0.0,x)
			self.imgScroll.scroll_x = x
		if self.imgRoll.width < self.imgScroll.width:
			self.imgScroll.scroll_x = 0.0
		if type(y) is float and newHeight>self.imgScroll.height:
			point = ((1-self.imgScroll.scroll_y)*(self.imgRoll.height-self.imgScroll.height)+y*self.imgScroll.height)/(self.imgRoll.height)
			point *= newHeight
			point -= y*self.imgScroll.height
			point /= (newHeight - self.imgScroll.height)
			y = 1 - point
			y = min(1.0,y)
			y = max(0.0,y)
			self.imgScroll.scroll_y = y
		if self.imgRoll.height < self.imgScroll.height:
			self.imgScroll.scroll_y = 1.0
		self.imgGrid.width = newWidth
		self.imgGrid.height = newHeight

	def stageSwitch(self,stage,instance=None,value=True,*args):
		if value:
			self.stageNow = stage
			if not self.stages[stage]["check"].active:
				print("make active",stage)
				self.stages[stage]["check"].active = True

	def updateSlider(self, slider, instance, value, *args):
		# print(self.sliders)
		if slider in self.sliders:
			# print(slider)
			self.sliders[slider]["val"] = value
			self.sliders[slider]["btn"].text = slider + "(" + str(self.sliders[slider]["val"]) + ")"
		else:
			return
		if slider == "prediction threshold":
			self.updateThreshold(instance, value)
		elif slider == "overlay alpha":
			self.updateAlpha(instance, value)
		elif slider == "click radius":
			self.updateRadii(instance, value)

	def updateThreshold(self, instance, value, *args):
		print("threshold " + str(value))

	def updateAlpha(self, instance, value, *args):
		print("alpha " + str(value))

	def updateRadii(self, instance, value, *args):
		print("radii " + str(value))

	def clickInCanvas(self,touch,*args):
		if not (touch.spos[0] < self.canvasXmax and touch.spos[0] > self.canvasXmin and touch.spos[1] < self.canvasYmax and touch.spos[1] > self.canvasYmin):
			print("early return")
			return
		if touch.button == "left" or touch.button == "right":
			x = (self.imgRoll.width - self.imgScroll.width)*self.imgScroll.scroll_x + self.imgScroll.width*(touch.spos[0]-self.canvasXmin)/(self.canvasXmax-self.canvasXmin)
			y = (self.imgRoll.height - self.imgScroll.height)*(1.0-self.imgScroll.scroll_y) + self.imgScroll.height*(self.canvasYmax-touch.spos[1])/(self.canvasYmax-self.canvasYmin)
			# x = (touch.spos[0]-self.canvasXmin)/(self.canvasXmax-self.canvasXmin)
			# point = (self.imgScroll.scroll_x*(self.imgRoll.width-self.imgScroll.width)+x*self.imgScroll.width)/(self.imgRoll.width)
			# print("point blah is ",point)
			# print("call",x,y)
			# print(self.imgRoll.width,self.imgScroll.width,self.imgScroll.scroll_x,touch.spos[0],self.canvasXmin,self.canvasXmax,self.canvasXmin)
			self.addPoint(x,y,touch.button == "left")
		elif touch.button == "scrollup":
			self.zoomDir("++",(touch.spos[0]-self.canvasXmin)/(self.canvasXmax-self.canvasXmin),(self.canvasYmax-touch.spos[1])/(self.canvasYmax-self.canvasYmin))
		elif touch.button == "scrolldown":
			self.zoomDir("--",(touch.spos[0]-self.canvasXmin)/(self.canvasXmax-self.canvasXmin),(self.canvasYmax-touch.spos[1])/(self.canvasYmax-self.canvasYmin))

	def addPoint(self,x,y,is_positive,*args):
		if not (x/self.zoomNow < self.imgWidth and y/self.zoomNow < self.imgHeight):
			print("outside",x,y,self.zoomNow)
			return
		print("point is ",x,y)
		cen_x = x/self.imgGrid.width
		cen_y = 1 - (y/self.imgGrid.height)
		w = self.sliders["click radius"]["val"]
		grid = FloatLayout(size_hint=(None,None),width=w,height=w,pos_hint={"center_x":cen_x,"center_y":cen_y})
		self.imgGrid.add_widget(grid)
		self.clicks.append(grid)
		with self.clicks[-1].canvas:
			if is_positive:
				Color(0,1,0,self.sliders["overlay alpha"]["val"])
			else:
				Color(0,0,1,self.sliders["overlay alpha"]["val"])
			print(self.imgGrid.height,self.imgGrid.width,"this is me")
			cir = Ellipse()
		self.clicks[-1].bind(pos=partial(self._image_bind,self.clicks[-1],cir),size=partial(self._image_bind,self.clicks[-1],cir))
		# self.add_click(int(round(x/self.zoomNow)),int(round(y/self.zoomNow)),is_positive) # function in myModel

		self.stages[self.stageNow][is_positive](round(x/self.zoomNow),round(y/self.zoomNow))








	def get_files(self,folder,exts=None,address=False):
		# files_fold = ([(i) for i in listdir(folder) if ("." in i)])
		files_fold = []
		for (dirpath, dirnames, filenames) in walk(folder):
			files_fold = filenames
			break
		files_fold.sort()
		files_ext = []
		if not (exts is None):
			if(type("s")==type(exts)):
				exts = [exts]
			for filename in files_fold:
				for ext in exts:
					if(filename.endswith(ext)):
						files_ext.append(filename)
		if(exts is None):
			files_ext = files_fold
		files = []
		for filename in files_ext:
			name = ''
			if(address):
				name += folder + "/"
			name += filename
			name = name.replace("//","/")
			files.append(name)
		return files

	def deep_files(self,folder,exts=None):
		all_files = get_files(folder,exts)
		folders = get_folders(folder,deep=True,address=True)
		# print(folders)
		for fold in folders:
			# print(fold[len(folder):])
			files = get_files(fold,exts)
			for file in files:
				all_files.append(fold[len(folder):] + file)
			# all_files += files
		return all_files

