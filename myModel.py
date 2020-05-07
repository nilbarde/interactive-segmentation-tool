from isegm.utils import exp
from isegm.inference import utils
from isegm.inference import clicker
from isegm.inference.predictors import get_predictor

import torch
from torchvision import transforms

from myApp.importer import *

import cv2
import numpy as np
from kivy.loader import Loader
from functools import partial

class myModel():
	def __init__(self):
		print("init myModel")

	def makeModel(self,*args):
		self.device = torch.device('cpu')
		self.norm_radius = 260

		self.model = self.loadModel(self.weightsPath,self.device,self.norm_radius)

		self.predictor_params = {'brs_mode': 'NoBRS'}
		self.net = self.model.to(self.device)

		self.predictor = get_predictor(self.net, device=self.device,
									   **self.predictor_params)

		self.clicker = clicker.Clicker()
		self.states = []

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
		self.image_saver()

	def image_saver(self,*args):
		pred = self.probs_history[-1][1]
		print((pred.shape),np.sum(pred),pred.dtype)
		print("xoxo")

		res = np.zeros((pred.shape[0],pred.shape[1],4),dtype="uint8")
		res[:,:,1] = (pred > 0.5)*255
		res[:,:,3] = (pred > 0.5)*128

		source = "res.png"
		cv2.imwrite(source,res)

		self.reloadMask(source)

	def reloadMask(self,source,*args):
		# source = "res2.png"
		Cache.remove('kv.image')
		Cache.remove('kv.texture')
		Cache.remove('kv.canvas')
		Cache.remove('kv.Rectangle')
		self.imgGrid.canvas.remove(self.mask)
		with self.imgGrid.canvas:
			self.mask = Rectangle(source=source,size=self.imgGrid.size)
		print(self.mask.texture.size,self.imgGrid.width,self.imgGrid.height)
		self.imgGrid.bind(pos=partial(self._image_bind,self.imgGrid,self.mask),size=partial(self._image_bind,self.imgGrid,self.mask))
		self.imgGrid.width = self.imgWidth*self.zoomNow
		self.imgGrid.height = self.imgHeight*self.zoomNow
		print("success",self.mask.texture.size)

	def loadModel(self,path,device,norm_radius,*args):
		return utils.load_is_model(path, device, cpu_dist_maps=True, norm_radius=norm_radius)


