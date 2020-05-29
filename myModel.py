from isegm.utils import exp
from isegm.inference import utils
from isegm.inference import clicker
from isegm.inference.predictors import get_predictor

import torch
from torchvision import transforms

from myApp.importer import *

import cv2
import numpy as np
from os.path import dirname, basename, exists, isfile
from os import makedirs
from kivy.loader import Loader
from functools import partial

class myModel():
	def __init__(self):
		self.image_nd = None
		print("init myModel")

	def makeModel(self,*args):
		self.device = torch.device('cpu')
		self.norm_radius = 260

		self.model = self.loadModel(self.weightsPath,self.device,self.norm_radius)

		self.predictor_params = {'brs_mode': 'NoBRS'}
		self.net = self.model.to(self.device)
		self.reset_predictor()

	def reset_predictor(self,*args):
		self.predictor = get_predictor(self.net, device=self.device,
									   **self.predictor_params)
		if self.image_nd is not None:
			self.predictor.set_input_image(self.image_nd)

		self.clicker = clicker.Clicker()
		self.probs_history = []
		self.states = []
		self.clicks = []

	def nucleiFinish(self,*args):
		if not len(self.probs_history):
			return
		self.object_count += 1
		print("total objects ",self.object_count)
		pred = self.probs_history[-1][1]>self.sliders["prediction threshold"]["val"]
		
		# self.all_results = np.where(self.all_results==[self.object_count,self.object_count,self.object_count,128],0,self.all_results)
		self.all_results[self.all_results[:,:,0]==self.object_count] = [0,0,0,0]

		# self.all_results[self.all_results==[self.object_count,self.object_count,self.object_count,128]] = 0
		self.all_results[pred] = [self.object_count,self.object_count,self.object_count,128]
		self.reset_predictor()

	def nucleiAdd(self,x,y,*args):
		print("nucleiAdd")
		self.nucleiFinish()
		self.add_click(x,y,True)

	def nucleiRemove(self,x,y,*args):
		print("nucleiRemove")

	def nucleiPartAdd(self,x,y,*args):
		print("nucleiPartAdd",x,y)
		self.add_click(x,y,True)

	def nucleiPartRemove(self,x,y,*args):
		print("nucleiPartRemove")
		self.add_click(x,y,False)

	def add_click(self, x, y, is_positive):
		print(x,y,is_positive)
		self.states.append({
			'clicker': self.clicker.get_state(),
			'predictor': self.predictor.get_states()
		})

		self.nucleiPoints.append([[x,y,is_positive]])
		click = clicker.Click(is_positive=is_positive, coords=(y, x))
		self.clicker.add_click(click)
		pred = self.predictor.get_prediction(self.clicker)
		torch.cuda.empty_cache()
		if self.probs_history:
			self.probs_history.append((self.probs_history[-1][0], pred))
		else:
			self.probs_history.append((np.zeros_like(pred), pred))
		pred = self.probs_history[-1][1]>self.sliders["prediction threshold"]["val"]
		# self.all_results[self.all_results==[self.object_count+1,self.object_count+1,self.object_count+1,128]] = 0
		# x = np.where(self.all_results[:,:,0]==self.object_count+1,0,self.all_results[:,:,0])
		self.all_results[self.all_results[:,:,0]==self.object_count+1] = [0,0,0,0]
		self.all_results[pred] = [self.object_count+1,self.object_count+1,self.object_count+1,128]
		self.image_saver()

	def undo_click(self):
		if not self.states:
			return

		self.imgGrid.remove_widget(self.clicks[-1])
		self.clicks.pop()
		prev_state = self.states.pop()
		self.clicker.set_state(prev_state['clicker'])
		self.predictor.set_states(prev_state['predictor'])
		self.nucleiPoints.pop()
		self.probs_history.pop()
		self.image_saver()

	def image_saver(self,*args):
		if not self.probs_history:
			self.imgGrid.canvas.remove(self.mask)
			with self.imgGrid.canvas:
				Color(0,0,0,0)
				self.mask = Rectangle(size=self.imgGrid.size)
			self.imgGrid.bind(pos=partial(self._image_bind,self.imgGrid,self.mask),size=partial(self._image_bind,self.imgGrid,self.mask))
			return
		pred = self.probs_history[-1][1]

		res = np.zeros((pred.shape[0],pred.shape[1],4),dtype="uint8")
		res[:,:,2] = (pred > 0.5)*255
		res[:,:,3] = (pred > 0.5)*128

		source = "res.png"
		cv2.imwrite(source,res)


		name = self.images[self.imageNow]
		end_name = basename(name)
		ext = end_name.split(".")[1]
		source = dirname(name) + "/results/" + end_name[:-len(ext)] + "png"
		folder = dirname(source)
		if not exists(folder):
			makedirs(folder)
		res = self.all_results
		cv2.imwrite(source,res)

		self.reloadMask(source)

	def reloadMask(self,source,*args):
		# source = "res2.png"
		Cache.remove('kv.image')
		Cache.remove('kv.texture')
		Cache.remove('kv.canvas')
		Cache.remove('kv.Rectangle')

		if not isfile(source):
			img = np.zeros((self.imgHeight, self.imgWidth,4),dtype="uint8")
			cv2.imwrite(source,img)

		temp_fold = "./temp/"
		if not exists(temp_fold):
			makedirs(temp_fold)

		mask = cv2.imread(source,-1)
		mask[:,:,2] = (mask[:,:,2]>0)*255
		mask[:,:,:2] = 0
		dummy_source = temp_fold + "x.png"
		cv2.imwrite(dummy_source,mask)

		self.imgGrid.canvas.remove(self.mask)
		with self.imgGrid.canvas:
			Color(1,0,0,0.5) # self.sliders["overlay alpha"]["val"]
			self.mask = Rectangle(source=dummy_source,size=self.imgGrid.size)
		self.imgGrid.bind(pos=partial(self._image_bind,self.imgGrid,self.mask),size=partial(self._image_bind,self.imgGrid,self.mask))

		self.sMaskGrid.canvas.remove(self.sMask)
		with self.sMaskGrid.canvas:
			Color(2.55,0,0,1)
			self.sMask = Rectangle(source=dummy_source,size=self.sMaskGrid.size)
		self.sMaskGrid.bind(pos=partial(self._image_bind,self.sMaskGrid,self.sMask),size=partial(self._image_bind,self.sMaskGrid,self.sMask))


	def loadPreMask(self,source,*args):
		img = cv2.imread(source)

		instances = np.max(img)
		# img *= 50

		for instance in range(1,instances+1):
			lower = (np.array([instance,instance,instance]))
			upper = (np.array([instance,instance,instance]))
			mask = cv2.inRange(img,lower,upper)
			cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL,
				cv2.CHAIN_APPROX_SIMPLE)
			# cnts = imutils.grab_contours(cnts)
			cnts = imutils.grab_contours(cnts)

			for c in cnts:
				# compute the center of the contour
				M = cv2.moments(c)
				if True:
					cX = int(M["m10"] / M["m00"])
					cY = int(M["m01"] / M["m00"])
					# draw the contour and center of the shape on the img
					is_positive = True
					self.nucleiPoints.append([[cX,cY,is_positive]])
					w = self.sliders["click radius"]["val"]
					grid = FloatLayout(size_hint=(None,None),width=w,height=w,pos_hint={"center_x":cX*1.0/self.imgWidth,"center_y":1.0-(cY*1.0/self.imgHeight)})
					self.imgGrid.add_widget(grid)
					self.object_count += 1
					self.clicks.append(grid)
					with self.clicks[-1].canvas:
						if is_positive:
							Color(0,1,0,self.sliders["overlay alpha"]["val"])
						else:
							Color(0,0,1,self.sliders["overlay alpha"]["val"])
						cir = Ellipse()
					self.clicks[-1].bind(pos=partial(self._image_bind,self.clicks[-1],cir),size=partial(self._image_bind,self.clicks[-1],cir))
					click = clicker.Click(is_positive=is_positive, coords=(cY, cX))
					self.clicker.add_click(click)
				else:
					pass


	def loadModel(self,path,device,norm_radius,*args):
		return utils.load_is_model(path, device, cpu_dist_maps=True, norm_radius=norm_radius)


