import numpy as np
import scipy.stats as st
from sklearn.neural_network import MLPRegressor

class EsembleNNet:
	def __init__(self, n_estimators = 100, n_neurons = 1, n_new_estimators = 10, bag_size = 1):

		self.estimators_		= []

		self.n_estimators	 = n_estimators
		self.n_neurons		= n_neurons
		self.n_new_estimators = n_new_estimators
		self.bag_size		 = bag_size
		self.epsilon			= 0.0
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

		acc = []
		for e in self.estimators_:
			nrmse = self.nrmse(y, e.predict(x))

			if nrmse > 1:
				acc.append(0)
			else:
				acc.append(1. - nrmse)

		acc = np.array(acc)

		if np.sum(acc) > 0:
			self.w = acc / np.sum(acc) if np.sum(self.w) == 0 else self.w * self.epsilon + (1. - self.epsilon) * acc / np.sum(acc)

		# This kills the weighting
		self.w = np.ones((1, self.n_estimators)) / self.n_estimators
 
		return

	def fit(self, x, y):
		# Fits the training set data and enables warm_start for following updates on the model

		_x = self.feature_scaling_trainingset(x)

		for _ in range(self.n_estimators):

			e = MLPRegressor(
				solver = "lbfgs", alpha = 1e-5, hidden_layer_sizes = (self.n_neurons,), random_state = 1
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
		print("y_hat = {}".format(np.sort(y_hat[:, 0])))

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

		n_estimators = len(self.estimators_)

		estimators_	= []
		n = 0 # no. of estimatiors that will be removed
		for i in range(n_estimators):
			if err[i] < threshold or n > self.n_new_estimators:
				estimators_.append(self.estimators_[i])
			else:
				n = n + 1

		self.estimators_ = estimators_

		return



class EnsembleNNetSOMAC:

	def __init__(self, n_post_prunning = 10):

		# Variables:
		#	1. n_post_prunning: number of samples no
		self.n_post_prunning = n_post_prunning

		self.csma = EsembleNNet(n_estimators = 100)
		self.tdma = EsembleNNet(n_estimators = 100)

		# Mapping metrics names to ids
		self.map_metric = {
			'thr': 0, 'lat': 1, 'jit': 2, 'rnp': 3, 'interpkt': 4, 'snr': 5, 'contention': 6, 'non': 7, 'bsz': 8
		}
		self.map_aggr = {
			'sum': 0, 'avg': 1, 'max': 2, 'min': 3, 'var': 4, 'count': 5
		}

		# Metrics that will be used by the ML algorithm
		self.in_metric = [
			"interpkt", "interpkt", "interpkt", "snr", "snr", "snr", "bsz", "bsz"
		]

		self.in_aggr = [
			"avg", "sum", "max", "min", "avg", "max", "avg", "sum"
		]

		self.out_metric = "thr"
		self.out_aggr	= "avg"

		# Data window
		# DWs are used for evaluation, post-prunning and training new trees to the model
		self.csma_dw_x = []
		self.csma_dw_y = []
		self.tdma_dw_x = []
		self.tdma_dw_y = []

		# UCB (Upper-Confidence-Bound) parameters
		# This first set of parameters are argument of log() and denominators, so must be > 0
		self.n_csma	= 1
		self.n_tdma	= 1
		self.t		 = 1

		self.c		 = 5 # this value should be evaluated

		self.rmse_csma = 0
		self.rmse_tdma = 0

		return

	def train(self, file):
		# Trains the regressors of both CSMA and TDMA

		self.data = np.load(file, encoding = "latin1").item()

		x_csma, y_csma = self._get_xy("CSMA")
		x_tdma, y_tdma = self._get_xy("TDMA")

		self.csma.fit(x_csma, y_csma)
		self.tdma.fit(x_tdma, y_tdma)

		return

	def _get_xy(self, prot):
		# Splits the training data set according to input metrics and protocol

		map_prot = lambda _p: 0 if _p == "CSMA" else 1

		tsteps = [t for t in self.data if self.data[t]["prot"] == map_prot(prot)]

		y = [
			self.data[t]["metrics"][self.map_metric[self.out_metric], self.map_aggr[self.out_aggr]]
			for t in tsteps
		]

		x = []
		for t in tsteps:
			row = [
				self.data[t]["metrics"][self.map_metric[met], self.map_aggr[aggr]]
				for (met, aggr) in (zip(self.in_metric, self.in_aggr))
			]

			# dt and transition seem not interfer a lot
			#row.extend([self.data[t]["dt"], self.data[t]["transition"] * 1.])

			x.append(row)

		return np.array(x), np.array(y)

	def decision(self, arr):
		# Decision made based on UCB (Upper-Confidence-Bound) principle
		# prot = argmax(CSMA, TDMA), thinking abouth throughput

		curr_prot = arr["prot"]
		x = np.array([[arr["metrics"][self.map_metric[met], self.map_aggr[aggr]]
			 for (met, aggr) in (zip(self.in_metric, self.in_aggr))
		]])
		y = arr["metrics"][self.map_metric["thr"], self.map_aggr["avg"]]

		y_hat_csma = self.csma.predict(x)
		y_hat_tdma = self.tdma.predict(x)

		print("Prot: {}, y = {}".format(arr["prot"], y))
		print("y_hat_CSMA = {}, y_hat_TDMA = {}".format(round(y_hat_csma, 2), round(y_hat_tdma, 2)))

		# UCB based decision
		v_csma = float(y_hat_csma - self.rmse_csma + self.c * np.sqrt(np.log(self.t) / self.n_csma))
		v_tdma = float(y_hat_tdma - self.rmse_tdma + self.c * np.sqrt(np.log(self.t) / self.n_tdma))

		prot	= np.argmax([v_csma, v_tdma])

		print("Evaluation: v_csma = {}, v_tdma = {}".format(round(v_csma, 2), round(v_tdma, 2)))

		ratio = 0
		if v_csma > 0 and v_tdma > 0:
			ratio = v_csma/v_tdma if v_csma > v_tdma else v_tdma/v_csma

		gain = ratio - 1. if ratio > 1. else 0

		# Update parameters of UCB
		self.t = self.t + 1
		if curr_prot == 0:	# CSMA
			self.n_csma = self.n_csma + 1

			self.csma_dw_x.extend([list(x[0])])
			self.csma_dw_y.extend([y])

		elif curr_prot == 1: # TDMA
			self.n_tdma = self.n_tdma + 1

			self.tdma_dw_x.extend([list(x[0])])
			self.tdma_dw_y.extend([y])

		# Evaluate regressors
		# If necessary, post-prunning and retraining is made
		self.eval_reg()

		return prot, ratio - 1.

	def eval_reg(self):
		# Check if it is time for prunning
		# if so, prunning & retraining is made

		if len(self.csma_dw_y) >= self.n_post_prunning:
			x = np.array(self.csma_dw_x)
			y = np.array(self.csma_dw_y)

			self.csma.post_prunning(x, y, 0.6)
			self.csma.update(x, y)

			self.csma_dw_x, self.csma_dw_y = [], []

		if len(self.tdma_dw_y) >= self.n_post_prunning:
			x = np.array(self.tdma_dw_x)
			y = np.array(self.tdma_dw_y)

			self.tdma.post_prunning(x, y, 0.3)
			self.tdma.update(x, y)

			self.tdma_dw_x, self.tdma_dw_y = [], []

		return
