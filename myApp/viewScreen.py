from .importer import *

class viewScreen:
	def __init__(self):
		print("init viewScreen")

	def loadScreen(self,*args):
		self.setDimensions()
		self.clear_widgets()

		# inserting image field
		self.setImageScroll()

		# inputs
		for inputName in self.inputs:
			grid = GridLayout(cols=2,size_hint=self.inputs[inputName]["dim"],pos_hint=self.inputs[inputName]["pos"],spacing=0,padding=0)
			self.add_widget(grid)

			self.inputs[inputName]["input"] = TextInput(text=self.inputs[inputName]["val"] ,font_size=25, size_hint = (0.6,1.0))
			grid.add_widget(self.inputs[inputName]["input"])
			self.inputs[inputName]["btn"] = Button(text=inputName,font_size=25,size_hint=(0.4,1.0),on_press=self.inputs[inputName]["fun"])
			grid.add_widget(self.inputs[inputName]["btn"])

		# buttons
		for btn in self.btns:
			self.btns[btn]["btn"] = Button(text=btn,font_size=30,size_hint=self.btns[btn]["dim"],pos_hint=self.btns[btn]["pos"],on_press=self.btns[btn]["fun"])
			# self.btns[btn]["btn"].bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
			self.add_widget(self.btns[btn]["btn"])

		# sliders
		self.sliderScroll, self.sliderRoll = self.getRoll(size_hint=self.sliderGridDim,pos_hint=self.sliderGridPos,grid=self,direction="ver")
		for slider in self.sliders:
			grid = GridLayout(cols=1,size_hint=(1.0,None),spacing=2,padding=15)
			grid.bind(minimum_height=grid.setter('height'))
			self.sliderRoll.add_widget(grid)

			self.sliders[slider]["btn"] = Button(text=slider + "(" + str(self.sliders[slider]["val"]) + ")" ,font_size=30, size_hint = (1.0,None), height=60)
			grid.add_widget(self.sliders[slider]["btn"])
			self.sliders[slider]["slider"] = Slider(min=self.sliders[slider]["min"], max=self.sliders[slider]["max"], value=self.sliders[slider]["val"], orientation='horizontal', step=self.sliders[slider]["step"], size_hint = (1.0,None), height=80)
			self.sliders[slider]["slider"].bind(value=partial(self.sliders[slider]["fun"]))
			grid.add_widget(self.sliders[slider]["slider"])

		# stages
		self.stagesScroll, self.stagesRoll = self.getRoll(size_hint=self.stagesGridDim,pos_hint=self.stagesGridPos,grid=self,direction="ver")
		print("stages")
		for stage in self.stages:
			grid = GridLayout(cols=2,size_hint=(1.0,None),spacing=2,padding=15)
			grid.bind(minimum_height=grid.setter('height'))
			self.stagesRoll.add_widget(grid)

			self.stages[stage]["check"] = CheckBox(size_hint=(0.2,None), height=60,group="stages")
			self.stages[stage]["check"].bind(active=self.stages[stage]["fun"])
			grid.add_widget(self.stages[stage]["check"])
			self.stages[stage]["btn"] = Button(text=self.stages[stage]["task"],font_size=30, size_hint = (0.8,None), height=60, on_press=partial(self.stages[stage]["fun"],None,True))
			grid.add_widget(self.stages[stage]["btn"])

	def setImageScroll(self,*args):
		grid = FloatLayout(size_hint=self.imgDim, pos_hint=self.imgPos)
		self.add_widget(grid)

		self.imgScroll = ScrollView(size_hint=(self.imgRatioWidth,self.imgRatioHeight),pos_hint={"center_x":self.imgRatioWidth/2,"center_y":1-(self.imgRatioHeight/2)}, size=(grid.width, grid.height),do_scroll_y=False)
		grid.add_widget(self.imgScroll)

		self.imgRoll = GridLayout(cols=1, size_hint_y=None, size_hint_x=None, spacing=2, padding=2)
		self.imgRoll.bind(minimum_height=self.imgRoll.setter('height'))
		self.imgRoll.bind(minimum_width=self.imgRoll.setter('width'))
		self.imgScroll.add_widget(self.imgRoll)

		self.imgScrollerY = Slider(min=0, max=1, value=1, orientation='vertical',   step=0.01, size_hint=(1 - self.imgRatioWidth, self.imgRatioHeight), pos_hint={"center_x":1 - (1 - self.imgRatioWidth)/2,"center_y":1-(self.imgRatioHeight/2)})
		grid.add_widget(self.imgScrollerY)
		self.imgScrollerX = Slider(min=0, max=1, value=0, orientation='horizontal', step=0.01, size_hint=(self.imgRatioWidth, 1 - self.imgRatioHeight), pos_hint={"center_x":self.imgRatioWidth/2,"center_y":(1 - self.imgRatioHeight)/2})
		grid.add_widget(self.imgScrollerX)

		self.imgScrollerY.bind(value=partial(self.sliderScrolled, self.imgScroll, "y"))
		self.imgScrollerX.bind(value=partial(self.sliderScrolled, self.imgScroll, "x"))

		self.imgScroll.bind(scroll_y=partial(self.imgScrolled, self.imgScrollerY))
		self.imgScroll.bind(scroll_x=partial(self.imgScrolled, self.imgScrollerX))

	def _image_bind(self,grid,thumb,*args):
		thumb.pos = grid.pos
		thumb.size = grid.size

	def sliderScrolled(self, scrl, direction, instance, value):
		if direction == "x":
			scrl.scroll_x = value
		elif direction == "y":
			scrl.scroll_y = value

	def imgScrolled(self, s, instance, value):
		if value >= 0:
		#this to avoid 'maximum recursion depth exceeded' error
			s.value=value
