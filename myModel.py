from isegm.utils import exp
from isegm.inference import utils
from isegm.inference import clicker
from isegm.inference.predictors import get_predictor

import torch
from torchvision import transforms

from myApp.importer import *

import cv2
import numpy as np
from os.path import dirname, basename, exists
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
		self.object_count += 1

		pred = self.probs_history[-1][1]>self.sliders["prediction threshold"]["val"]
		print(self.all_results.shape,pred.shape)
		self.all_results[pred] = self.object_count
		self.reset_predictor()

	def nucleiAdd(self,x,y,*args):
		self.nucleiFinish()
		self.add_click(x,y,True)
		print("nucleiAdd")

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

		click = clicker.Click(is_positive=is_positive, coords=(y, x))
		self.clicker.add_click(click)
		pred = self.predictor.get_prediction(self.clicker)
		torch.cuda.empty_cache()
		if self.probs_history:
			self.probs_history.append((self.probs_history[-1][0], pred))
		else:
			self.probs_history.append((np.zeros_like(pred), pred))
		pred = self.probs_history[-1][1]>self.sliders["prediction threshold"]["val"]
		self.all_results[pred] = (self.object_count+1)
		self.image_saver()

	def undo_click(self):
		print(self.states)
		if not self.states:
			return

		self.imgGrid.remove_widget(self.clicks[-1])
		self.clicks.pop()
		prev_state = self.states.pop()
		self.clicker.set_state(prev_state['clicker'])
		self.predictor.set_states(prev_state['predictor'])
		print(len(self.probs_history),"length")
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

		self.reloadMask(source)

		name = self.images[self.imageNow]
		source = dirname(name) + "/results/" + basename(name)
		folder = dirname(source)
		if not exists(folder):
			makedirs(folder)
		res = self.all_results
		cv2.imwrite(source,res)

	def reloadMask(self,source,*args):
		# source = "res2.png"
		Cache.remove('kv.image')
		Cache.remove('kv.texture')
		Cache.remove('kv.canvas')
		Cache.remove('kv.Rectangle')

		self.imgGrid.canvas.remove(self.mask)
		with self.imgGrid.canvas:
			Color(2.55,0,0,1)
			self.mask = Rectangle(source=source,size=self.imgGrid.size)
		self.imgGrid.bind(pos=partial(self._image_bind,self.imgGrid,self.mask),size=partial(self._image_bind,self.imgGrid,self.mask))

		self.sMaskGrid.canvas.remove(self.sMask)
		with self.sMaskGrid.canvas:
			Color(2.55,0,0,1)
			self.sMask = Rectangle(source=source,size=self.sMaskGrid.size)
		self.sMaskGrid.bind(pos=partial(self._image_bind,self.sMaskGrid,self.sMask),size=partial(self._image_bind,self.sMaskGrid,self.sMask))

	def loadModel(self,path,device,norm_radius,*args):
		print(path,device)
		return utils.load_is_model(path, device, cpu_dist_maps=True, norm_radius=norm_radius)


