# André Gomes <andre.gomes@dcc.ufmg.br>
# The Federal University of Minas Gerais <ufmg.br>

import numpy as np
import scipy.stats as st
from sklearn.ensemble import RandomForestRegressor

class RandomForest:
	# This class implements the ensemble ML method Random Forest
	# This is part of the SOMAC framework
	# The forest is continuously evaluated and post prunned when it is necessary
	# Trees that are inaccurate by some extent are removed and brand new ones are added
	# There 2 regressors implemented withing this class, 1 for CSMA and another for TDMA

	def __init__(self, n_estimators = 100, max_depth = 2, max_features = "log2", n_new_estimators = 10):
		
		self.reg = RandomForestRegressor(
			max_depth = max_depth, random_state = 0, n_estimators = n_estimators,
			warm_start = False, bootstrap = True, max_features = max_features, 
			min_samples_leaf = 3
		)

		self.n_estimators     = n_estimators
		self.n_new_estimators = n_new_estimators
		self.w                = np.zeros((1, n_estimators))

		return
	
	def feature_scaling_trainingset(self, x):
		# Feature scaling based on (x - x_avg) / x_avg
		# This is related to the training set, so it returns x_avg
		
		_x		 = np.zeros(x.shape)
		self.x_avg = np.zeros(x.shape[1])
		
		for col in range(x.shape[1]):
			self.x_avg[col] = np.mean(x[:, col])

			if self.x_avg[col] != 0:
				_x[:, col] = (x[:, col] - self.x_avg[col]) * 1. / self.x_avg[col]
			else:
				_x[:, col] = (x[:, col] - self.x_avg[col])

		return _x
	
	def feature_scaling(self, x):
		# Feature scales the input data according to self.x_avg (training set)
		
		_x = np.zeros(x.shape)
		
		for col in range(x.shape[1]):
			if self.x_avg[col] != 0:
				_x[:, col] = (x[:, col] - self.x_avg[col]) * 1. / self.x_avg[col]
			else:
				_x[:, col] = (x[:, col] - self.x_avg[col])
				
		return _x	  

	def calc_weights(self, x, y):
		# Updates the weights according to the accuracy of each predictor

		err = []
		epsilon = 1e-3
		for e in self.reg.estimators_:
			err.append(self.mae(y, e.predict(x)))

		err = np.array(err)

		num = 1 / (err + epsilon)
		den = np.sum(num)

		self.w = num / den

		self.w = np.ones(self.w.shape)
 
		return

	def update_weights(self, x, y, update_rate = 0.1):
		# Updates the weights in a Gradient Descent fashion

		_x = self.feature_scaling(x)

		loss = lambda y, h: float((y - h)**2)
		hypo = lambda w, e: np.dot(w, e.T) / (e.shape[1] * 1.)

		y_estimators = np.array([[float(e.predict(_x)) for e in self.reg.estimators_]])

		h = hypo(self.w, y_estimators)

		J = loss(y, h)

		dJ = (h - y) * y_estimators

		self.w = self.w - update_rate * dJ

		return

	def _me(self, y = 0, y_hat = 0):
		# Mean Error

		ME = np.mean(y - y_hat) / len(y)

		return ME

	def fit(self, x, y):
		# Fits the training set data and enables warm_start for following updates on the model
		
		_x = self.feature_scaling_trainingset(x)
		
		self.reg.fit(_x, y)

		#self.nrmse = np.mean([self._nrmse(y, e.predict(_x)) for e in self.reg.estimators_])

		self.calc_weights(_x, y)
		#self.err = np.mean([np.mean(y - e.predict(_x)) for e in self.reg.estimators_])

		y_hat = self.reg.predict(_x)
		self.me = self._me(y, y_hat)

		self.reg.set_params(warm_start = True)
		
		return
	
	def predict(self, x):
		# Final prediction, based on the entire set of estimators
		
		_x = self.feature_scaling(x)
		
		#y_hat = self.reg.predict(_x)

		y_hat = np.array([[e.predict(_x) for e in self.reg.estimators_]])

		print("y_hat.shape = {}".format(y_hat.shape))

		y_hat = np.dot(self.w, y_hat.T) / (y_hat.shape[1] * 1.)

		return y_hat
	
	def _nrmse(self, y, y_hat):
		# Computes the normalized root mean square error
		
		nrmse = 0
		y_avg = np.mean(y)
		n     = len(y)
		
		assert(n > 0), "len(y) must be greater than 0"
		
		if y_avg != 0:
			nrmse = np.sqrt(np.sum((y - y_hat)**2) / n) / y_avg
		else:
			nrmse = np.sqrt(np.sum((y - y_hat)**2) / n)
			
		return nrmse
	
	def rmse(self, y, y_hat):
		# Computes the root mean square error
		
		rmse = 0
		n	= len(y)
		
		assert(n > 0), "len(y) must be greater than 0"
		
		rmse = np.sqrt(np.sum((y - y_hat)**2) / n)
		
		return rmse

	def mae(self, y, y_hat):
		# Mean Absolute Error
		MAE = np.sum(np.abs(y - y_hat)) / len(y)

		return MAE
		
	def post_prunning(self, x, y, threshold):
		# This method removes trees less accurate than a give threshold
		# The threshold should be based on NRMSE
		# Max. no. of estimators to prune: self.n_new_estimators
		# This does NOT update the model with new trees
		
		_x = self.feature_scaling(x)
		
		err           = np.array([self._nrmse(y, e.predict(_x)) for e in self.reg.estimators_])
		argerr        = np.argsort(err)
		sorted_argerr = [argerr[i] for i in range(len(err) - 1, -1, -1)]

		n_estimators = len(self.reg.estimators_)

		estimators_ = []
		n = 0 # no. of estimatiors that will be removed
		for idx in sorted_argerr:
			if err[idx] < threshold or n >= self.n_new_estimators:
				estimators_.append(self.reg.estimators_[idx])
			else:
				n = n + 1
  
		self.reg.estimators_ = estimators_
		
		return
	
	def update(self, x, y):
	  # Given a pruned forest, it inserts new trees based on new data
		
		_x = self.feature_scaling(x)
		
		if len(self.reg.estimators_) < self.reg.n_estimators:
			print("No. of new estimators = {}".format(self.reg.n_estimators - len(self.reg.estimators_)))
			self.reg.fit(_x, y)

			nrmse = np.mean([self._nrmse(y, e.predict(_x)) for e in self.reg.estimators_])

			#self.nrmse = self.nrmse * 0.75 + 0.25 * nrmse
			#self.err = np.mean([np.mean(y - e.predict(_x)) for e in self.reg.estimators_])

			#self.calc_weights(_x, y)

			# Update Mean Error
			y_hat = self.predict(x)
			alpha = 0.75
			self.me = self.me * alpha + (1. - alpha) * self._me(y, y_hat)

		else:
			print("No update. Forest is already full.")
			
		return
