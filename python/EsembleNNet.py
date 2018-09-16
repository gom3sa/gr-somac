import numpy as np
import scipy.stats as st
from sklearn.neural_network import MLPRegressor

class EsembleNNet:
	def __init__(self, n_estimators = 100, n_neurons = 5, n_new_estimators = 10, bag_size = 0.6):

		self.estimators_	  = []

		self.n_estimators	  = n_estimators
		self.n_neurons		  = n_neurons
		self.n_new_estimators = n_new_estimators
		self.bag_size		  = bag_size
		self.w			      = np.zeros((1, n_estimators))

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

	def nrmse(self, y, y_hat):
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

	def mae(self, y, y_hat):
		# Mean Absolute Error
		MAE = np.sum(np.abs(y - y_hat)) / len(y)

		return MAE

	def bagging(self, x, y):

		_x = []
		_y = []
		n	= len(y)
		opts = np.arange(n) # options

		for _ in range(int(self.bag_size * n)):
			idx = np.random.choice(opts)

			_x.append(x[idx, :])
			_y.append(y[idx])

		return np.array(_x), np.array(_y)

	def update_weights(self, x, y):
		# Updates the weights according to the accuracy of each predictor

		err = []
		epsilon = 1e-1
		for e in self.estimators_:
			err.append(self.mae(y, e.predict(x)))

		err = np.array(err)

		num = (1 / (err + epsilon))
		den = np.sum(num)

		self.w = num / den
 
		return

	def fit(self, x, y):
		# Fits the training set data and enables warm_start for following updates on the model

		_x = self.feature_scaling_trainingset(x)

		for _ in range(self.n_estimators):

			e = MLPRegressor(
				solver = "lbfgs", alpha = 1e-4, max_iter = 1000, hidden_layer_sizes = (self.n_neurons,), random_state = 1
			)

			batch_x, batch_y = self.bagging(_x, y)
			e.fit(batch_x, batch_y)

			self.estimators_.append(e)

		self.update_weights(_x, y)

		return

	def predict(self, x):
		# Final prediction, based on the entire set of estimators

		_x = self.feature_scaling(x)

		y_hat = np.array([e.predict(_x) for e in self.estimators_])

		# Confidence Interval
		#print("Confidence Interval = {}, {}".format(lower, upper))
		#print("y_hat = {}".format(np.sort(y_hat[:, 0])))

		#print("w = {}".format(self.w))
		#print("y_hat = {}".format(y_hat))

		y_hat = np.dot(self.w, y_hat)

		return float(y_hat)

	def update(self, x, y):
		# Given a pruned forest, it inserts new trees based on new data

		_x = self.feature_scaling(x)

		if len(self.estimators_) < self.n_estimators:
			print("No. of new estimators = {}".format(self.n_estimators - len(self.estimators_)))

			n = self.n_estimators - len(self.estimators_)

			for _ in range(n):

				e = MLPRegressor(
					solver = "lbfgs", alpha = 1e-5, hidden_layer_sizes = (self.n_neurons,), random_state = 1
				)

				batch_x, batch_y = self.bagging(_x, y)

				e.fit(batch_x, batch_y)

				self.estimators_.append(e)

			self.update_weights(_x, y)

		else:
			print("No update. Forest is already full.")

		return

	def post_prunning(self, x, y, threshold):
		# This method removes trees less accurate than a give threshold
		# The threshold should be based on NRMSE
		# Max. no. of estimators to prune: self.n_new_estimators
		# This does NOT update the model with new trees

		_x = self.feature_scaling(x)

		err = np.array([self.nrmse(y, e.predict(_x)) for e in self.estimators_])

		n_estimators  = len(self.estimators_)
		argerr        = np.argsort(err)
		sorted_argerr = [argerr[i] for i in range(len(err) - 1, -1, -1)]

		n_estimators = len(self.estimators_)

		estimators_	= []
		n = 0 # no. of estimatiors that will be removed
		for i in sorted_argerr:
			if err[i] < threshold or n >= self.n_new_estimators:
				estimators_.append(self.estimators_[i])
			else:
				n = n + 1

		self.estimators_ = estimators_

		return