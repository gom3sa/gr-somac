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

		self.n_estimators	 = n_estimators
		self.n_new_estimators = n_new_estimators
		self.w				= np.zeros((1, n_estimators))

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

	def update_weights(self, x, y):
		# Updates the weights according to the accuracy of each predictor

		err = []
		epsilon = 1e-3
		for e in self.reg.estimators_:
			err.append(self.mae(y, e.predict(x)))

		err = np.array(err)

		num = 1 / (err + epsilon)
		den = np.sum(num)

		self.w = num / den
 
		return

	def fit(self, x, y):
		# Fits the training set data and enables warm_start for following updates on the model
		
		_x = self.feature_scaling_trainingset(x)
		
		self.reg.fit(_x, y)

		#self.nrmse = np.mean([self._nrmse(y, e.predict(_x)) for e in self.reg.estimators_])

		self.update_weights(_x, y)
		#self.err = np.mean([np.mean(y - e.predict(_x)) for e in self.reg.estimators_])

		self.reg.set_params(warm_start = True)
		
		return
	
	def predict(self, x):
		# Final prediction, based on the entire set of estimators
		
		_x = self.feature_scaling(x)
		
		#y_hat = self.reg.predict(_x)

		y_hat = np.array([e.predict(_x) for e in self.reg.estimators_])

		# Confidence Interval
		lower, upper = st.t.interval(0.95, len(y_hat) - 1, loc = np.mean(y_hat), scale = st.sem(y_hat))
		print("Confidence Interval = {}, {}".format(lower, upper))
		#print("y_hat = {}".format(np.sort(y_hat[:, 0])))

		n = len(y_hat)
		lower_idx = int(0.1 * n)
		upper_idx = int(0.9 * n)
		y_hat_sorted = np.sort(y_hat)
		y_hat_sorted = y_hat_sorted[lower_idx : upper_idx]
		print("y_hat_sorted mean = {}".format(round(np.mean(y_hat_sorted), 2)))

		y_hat = np.dot(self.w, y_hat)

		return float(y_hat)
	
	def _nrmse(self, y, y_hat):
		# Computes the normalized root mean square error
		
		nrmse = 0
		y_avg = np.mean(y)
		n	 = len(y)
		
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

		estimators_  = []
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

			self.update_weights(_x, y)

		else:
			print("No update. Forest is already full.")
			
		return