from os import walk
from .importer import *
from torchvision import transforms

class toolFunctions():
	def __init__(self):
		print("init toolFunctions")
		self.input_transform = transforms.Compose([
			transforms.ToTensor(),
			transforms.Normalize([.485, .456, .406], [.229, .224, .225])
		])

		x = 16
		colors = [[(i//(x**2))%x,(i//x)%x,i%x,8] for i in range(16**3)]
		colors = np.array(colors)*x
		permutation = np.random.permutation(colors.shape[0])
		self.colors = colors[permutation]
		self.colors[0] = [0,0,0,0]
		print(self.colors[143])

		self.folder_temp = "./temp/"

	def imageLoad(self,image_num=0,*args):
		print(image_num)
		if image_num >= len(self.imageNames) or image_num < 0:
			return

		self.imageNow = image_num
		self.name_image = self.imageNames[image_num]
		self.name_result = self.get_name_result(self.name_image)

		self.object_count = 0
		self.nucleiPoints = {}
		self.clicksCanvas = []
		self.clicksSub = []

		self.loadImageModel(self.name_image)
		self.loadImageScreen(self.name_image)
		self.loadResults(self.name_result)

		self.loadMask(self.result_image[:,:,0])
		self.loadClicks(self.nucleiPoints)
		self.showCenters(self.nucleiPoints)

		self.reset_predictor()

		self.zoomNow = 1
		self.isInstance = False
		self.nowInstance = 0

	def loadImageModel(self,name,*args):
		self.image = cv2.cvtColor(cv2.imread(name), cv2.COLOR_BGR2RGB)
		self.image_nd = self.input_transform(self.image).to(self.device)
		self.predictor.set_input_image(self.image_nd)

	def loadImageScreen(self,name,*args):
		self.imgGrid.canvas.clear()
		with self.imgGrid.canvas:
			self.img = Rectangle(source=name)
			self.imgWidth, self.imgHeight = (self.img.texture.size)
			self.imgGrid.width = self.imgWidth
			self.imgGrid.height = self.imgHeight
		self.imgGrid.bind(pos=partial(self._image_bind,self.imgGrid,self.img),size=partial(self._image_bind,self.imgGrid,self.img))

		copyfile(name,self.folder_temp + "img.png")

		img = "img"
		self.images[img]["grid"].canvas.clear()
		with self.images[img]["grid"].canvas:
			self.images[img]["rect"] = Rectangle()
		self.images[img]["rect"].texture = self.img.texture
		self.images[img]["grid"].bind(pos=partial(self._image_bind,self.images[img]["grid"],self.images[img]["rect"]),size=partial(self._image_bind,self.images[img]["grid"],self.images[img]["rect"]))

	def loadResults(self,source):
		if not isfile(source):
			img = np.zeros((self.imgHeight, self.imgWidth,3),dtype="uint8")
			self.ensure_dir(source)
			cv2.imwrite(source,img)
		else:
			img = cv2.imread(source)
		self.result_image = img
		centers = self.getContourCenters(img)
		self.nucleiPoints = {}
		for center in centers:
			x, y = centers[center]
			self.nucleiPoints[center] = {"center":[x, y],"points":[[x, y,True]]}
		self.object_count = np.max(img)

	def saveResults(self):
		cv2.imwrite(self.name_result,self.result_image)

	def getContourCenters(self,img,*args):
		instances = np.max(img)
		centers = {}

		print(instances)
		for instance in range(1,instances+1):
			lower = (np.array([instance,instance,instance]))
			upper = (np.array([instance,instance,instance]))
			mask = cv2.inRange(img,lower,upper)
			cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL,
				cv2.CHAIN_APPROX_SIMPLE)
			cnts = imutils.grab_contours(cnts)

			for c in cnts:
				M = cv2.moments(c)
				try:
					cX = int(M["m10"] / M["m00"])
					cY = int(M["m01"] / M["m00"])
					centers[instance] = [cX,cY]
				except:
					pass
		return centers

	def loadMask(self,image,*args):
		image=(self.colors[image.astype(int)])
		dummy_source = self.folder_temp + "x.png"
		self.ensure_dir(dummy_source)
		cv2.imwrite(dummy_source,image)

		try:
			self.imgGrid.canvas.remove(self.mask)
		except:
			pass

		Cache.remove('kv.image')
		Cache.remove('kv.texture')
		Cache.remove('kv.canvas')
		Cache.remove('kv.Rectangle')

		with self.imgGrid.canvas:
			self.mask = Rectangle(source=dummy_source,size=self.imgGrid.size)
		self.imgGrid.bind(pos=partial(self._image_bind,self.imgGrid,self.mask),size=partial(self._image_bind,self.imgGrid,self.mask))

		img = "seg"
		self.images[img]["grid"].canvas.clear()
		with self.images[img]["grid"].canvas:
			# Color(0,0,0,1)
			self.images[img]["rect"] = Rectangle(source=dummy_source)
		self.imgGrid.bind(pos=partial(self._image_bind,self.images[img]["grid"],self.images[img]["rect"]),size=partial(self._image_bind,self.images[img]["grid"],self.images[img]["rect"]))

	def loadClicks(self,nucleus,*args):
		img = "clk"
		self.images[img]["grid"].canvas.clear()

	def showCenters(self,nucleus):
		for click in self.clicksCanvas:
			self.imgGrid.remove_widget(click)
		for click in self.clicksSub:
			self.images["clk"]["grid"].remove_widget(click)

		for nuclei in nucleus:
			x,y = nucleus[nuclei]["center"]
			cen_x = x/self.imgGrid.width
			cen_y = 1 - (y/self.imgGrid.height)
			self.drawClick(cen_x,cen_y,True)

	def drawClick(self,cen_x,cen_y,is_positive,*args):
		w = self.sliders["click radius"]["val"]

		grid = FloatLayout(size_hint=(None,None),width=w,height=w,pos_hint={"center_x":cen_x,"center_y":cen_y})
		self.imgGrid.add_widget(grid)
		self.clicksCanvas.append(grid)
		with self.clicksCanvas[-1].canvas:
			if is_positive:
				Color(0,1,0,self.sliders["overlay alpha"]["val"])
			else:
				Color(0,0,1,self.sliders["overlay alpha"]["val"])
			cir = Ellipse()
		self.clicksCanvas[-1].bind(pos=partial(self._image_bind,self.clicksCanvas[-1],cir),size=partial(self._image_bind,self.clicksCanvas[-1],cir))

		grid = FloatLayout(size_hint=(None,None),width=w/4,height=w/4,pos_hint={"center_x":cen_x,"center_y":cen_y})
		self.images["clk"]["grid"].add_widget(grid)
		self.clicksSub.append(grid)
		with self.clicksSub[-1].canvas:
			if is_positive:
				Color(0,1,0,self.sliders["overlay alpha"]["val"])
			else:
				Color(0,0,1,self.sliders["overlay alpha"]["val"])
			cir = Ellipse()
		self.clicksSub[-1].bind(pos=partial(self._image_bind,self.clicksSub[-1],cir),size=partial(self._image_bind,self.clicksSub[-1],cir))

	def modelLoad(self,*args):
		self.weightsPath = self.inputs["model-weights path"]["input"].text
		self.makeModel()

	def imageNext(self,*args):
		self.nucleiFinish()
		self.imageLoad(self.imageNow+1)

	def imagePrev(self,*args):
		self.imageLoad(self.imageNow-1)

	def imageUndo(self,*args):
		self.undo_click()

	def imageReset(self,*args):
		self.imageLoad(self.imageNow)

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
			self.addPoint(x,y,touch.button == "left")
		elif touch.button == "scrollup":
			self.zoomDir("++",(touch.spos[0]-self.canvasXmin)/(self.canvasXmax-self.canvasXmin),(self.canvasYmax-touch.spos[1])/(self.canvasYmax-self.canvasYmin))
		elif touch.button == "scrolldown":
			self.zoomDir("--",(touch.spos[0]-self.canvasXmin)/(self.canvasXmax-self.canvasXmin),(self.canvasYmax-touch.spos[1])/(self.canvasYmax-self.canvasYmin))

	def addPoint(self,x,y,is_positive,*args):
		if not (x/self.zoomNow < self.imgWidth and y/self.zoomNow < self.imgHeight):
			print("outside",x,y,self.zoomNow)
			return
		self.stages[self.stageNow][is_positive](round(x/self.zoomNow),round(y/self.zoomNow))

	def updateCenters(self,*args):
		centers = self.getContourCenters(self.result_image)
		for center in centers:
			self.nucleiPoints[center]["center"] = centers[center]
		self.showCenters(self.nucleiPoints)

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















	def get_name_result(self,name):
		end_name = basename(name)
		ext = end_name.split(".")[1]
		return dirname(name) + "/results/" + end_name[:-len(ext)] + "png"

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

	def ensure_dir(self,file_path):
		if '/' in file_path:
			directory = dirname(file_path)
			if not exists(directory):
				makedirs(directory)
