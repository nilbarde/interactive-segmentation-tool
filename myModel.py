# from isegm.utils import exp
# from isegm.inference import utils
# from isegm.inference import clicker
# from isegm.inference.predictors import get_predictor

# import torch
# from torchvision import transforms
# import cv2

class myModel():
	def __init__(self):
		print("init myModel")

	def nucleiFromScratch(self,*args):
		print("model 1 - detecting from scratch")

	def nucleiAdd(self,x,y,*args):
		print("model 2 - add new nuclei at point - x : " + str(x) + ", y : " + str(y))

	def nucleiRemove(self,x,y,*args):
		print("model 2 - remove nuclei at point - x : " + str(x) + ", y : " + str(y))

	def nucleiPartAdd(self,x,y,*args):
		print("model 2/3 - improve by adding part at point - x : " + str(x) + ", y : " + str(y))

	def nucleiPartRemove(self,x,y,*args):
		print("model 2/3 - improve by removing part at point - x : " + str(x) + ", y : " + str(y))

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
		print((pred.shape),pred.dtype)
		print("xoxo")

		res = (pred > 0.5)*255
		cv2.imwrite("res.png",res)


		# if self.probs_history:
		# 	self.probs_history.append((self.probs_history[-1][0], pred))
		# else:
		# 	self.probs_history.append((np.zeros_like(pred), pred))

	def loadModel(self,path,device,norm_radius,*args):
		return utils.load_is_model(path, device, cpu_dist_maps=True, norm_radius=norm_radius)


