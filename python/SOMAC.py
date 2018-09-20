#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import logging

class SOMAC:

	def __init__(self, reg_csma, reg_tdma, n_post_prunning = 10):

		# Variables:
		#   1. n_post_prunning: number of samples no 
		self.n_post_prunning = n_post_prunning
		
		self.csma = reg_csma
		self.tdma = reg_tdma
		#self.csma = RandomForest(n_estimators = 50, max_depth = 5)
		#self.tdma = RandomForest(n_estimators = 50, max_depth = 5)
		
		# Mapping metrics names to ids
		self.map_metric = {
			'thr': 0, 'lat': 1, 'jit': 2, 'rnp': 3, 'interpkt': 4, 'snr': 5, 'contention': 6, 'non': 7, 'bsz': 8
		}
		self.map_aggr = {
			'sum': 0, 'avg': 1, 'max': 2, 'min': 3, 'var': 4, 'count': 5
		}
		
		# Metrics that will be used by the ML algorithm
		self.in_metric = [
			"interpkt", "interpkt", "bsz", "interpkt", "snr", "bsz", "snr"
		]

		self.in_aggr = [
			"avg", "sum", "sum", "max", "min", "avg", "var"
		]
		#self.in_metric = [
		#	"interpkt", "interpkt", "snr", "bsz", "bsz"
		#]

		#self.in_aggr = [
		#	"avg", "sum", "min", "avg", "sum"
		#]
		
		self.out_metric = "thr"
		self.out_aggr   = "avg"
		
		# Data window
		# DWs are used for evaluation, post-prunning and training new trees to the model
		self.csma_dw_x = []
		self.csma_dw_y = []
		self.tdma_dw_x = []
		self.tdma_dw_y = []
		
		# UCB (Upper-Confidence-Bound) parameters
		# This first set of parameters are argument of log() and denominators, so must be > 0
		self.n_csma    = 1
		self.n_tdma    = 1
		self.t	       = 1
		self.c         = 5 # this value should be evaluated
		
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
	
		# Update weights
		#if curr_prot == 0: # CSMA
		#	self.csma.update_weights(x, y, update_rate = 0.01)
		#elif curr_prot == 1: # TDMA
		#	self.tdma.update_weights(x, y, update_rate = 0.01)

		y_hat_csma = self.csma.predict(x)
		y_hat_tdma = self.tdma.predict(x)

		# Update Mean Error
		alpha = 0.9
		if curr_prot == 0:
			self.csma.me = self.csma.me * alpha + (1. - alpha) * self.csma._me(y - y_hat_csma)
		elif curr_prot == 1:
			self.tdma.me = self.tdma.me * alpha + (1. - alpha) * self.tdma._me(y - y_hat_tdma)

		logging.info("Prot: {}, y = {}".format(arr["prot"], y))
		logging.info("y_hat_CSMA = {}, y_hat_TDMA = {}".format(y_hat_csma, y_hat_tdma, 2))
		
		# Decision
		v_csma = float(y_hat_csma) + self.csma.me
		v_tdma = float(y_hat_tdma) + self.tdma.me
		
		prot  = np.argmax([v_csma, v_tdma])

		logging.info("Evaluation: v_csma = {}, v_tdma = {}".format(round(v_csma, 2), round(v_tdma, 2)))

		# Update parameters of UCB
		self.t = self.t + 1
		if curr_prot == 0:   # CSMA
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

		gain = 0.
		if v_csma != 0 and v_tdma != 0:
			gain = np.abs((v_csma - v_tdma) / v_csma) if v_csma > v_tdma \
				else np.abs((v_tdma - v_csma) / v_tdma)

		logging.info("Gain = {}".format(gain))
		
		return prot, gain, v_csma, v_tdma#y_hat_csma, y_hat_tdma
	
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
