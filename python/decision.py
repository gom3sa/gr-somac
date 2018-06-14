#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2018 André Gomes, UFMG - <andre.gomes@dcc.ufmg.br>.
# 
# This is free software you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy
from gnuradio import gr
import pmt
import time
import thread
import numpy as np
import copy as cp
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor as nnet
from sklearn import tree as dt
from sklearn import svm
from sklearn.neural_network import MLPClassifier

portid = 200 # Initially no MAC protocol is used. The normal node waits for coordinator's message.
threshold = 0.1 # Threshold for switching MAC protocol

class decision(gr.basic_block):
	"""
	MAC protocols:
		CSMA/CA:	portid = 0
		TDMA:		portid = 1
	"""
	def __init__(self, coord, dec_gran, broad_gran, metrics_gran, backlog_file, train_file, ml_alg, onoff_learn, \
			aggr0, aggr1, aggr2, aggr3, aggr4, aggr5, aggr6, aggr7): # {{{

		gr.basic_block.__init__(self, name="decision", in_sig=None, out_sig=None)

		self.coord = coord # Is coordinator? 
		self.dec_gran = dec_gran # Granularity of decision
		self.broad_gran = broad_gran
		self.metrics_gran = metrics_gran
		self.backlog_file = backlog_file
		self.train_file = train_file
		self.ml_alg = ml_alg
		self.onoff_learn = onoff_learn

		self.met0 = []
		self.met1 = []
		self.met2 = []
		self.met3 = []
		self.met4 = []
		self.met5 = []
		self.met6 = []
		self.met7 = []

		self.aggr0 = aggr0
		self.aggr1 = aggr1
		self.aggr2 = aggr2
		self.aggr3 = aggr3
		self.aggr4 = aggr4
		self.aggr5 = aggr5
		self.aggr6 = aggr6
		self.aggr7 = aggr7

		# Input ports
		self.msg_port_act_prot_in = pmt.intern('act prot in')
		self.message_port_register_in(self.msg_port_act_prot_in)
		self.set_msg_handler(self.msg_port_act_prot_in, self.act_prot_in)

		self.msg_port_met_in0 = pmt.intern('met in0')
		self.message_port_register_in(self.msg_port_met_in0)
		self.set_msg_handler(self.msg_port_met_in0, self.met_in0)

		self.msg_port_met_in1 = pmt.intern('met in1')
		self.message_port_register_in(self.msg_port_met_in1)
		self.set_msg_handler(self.msg_port_met_in1, self.met_in1)

		self.msg_port_met_in2 = pmt.intern('met in2')
		self.message_port_register_in(self.msg_port_met_in2)
		self.set_msg_handler(self.msg_port_met_in2, self.met_in2)

		self.msg_port_met_in3 = pmt.intern('met in3')
		self.message_port_register_in(self.msg_port_met_in3)
		self.set_msg_handler(self.msg_port_met_in3, self.met_in3)

		self.msg_port_met_in4 = pmt.intern('met in4')
		self.message_port_register_in(self.msg_port_met_in4)
		self.set_msg_handler(self.msg_port_met_in4, self.met_in4)

		self.msg_port_met_in5 = pmt.intern('met in5')
		self.message_port_register_in(self.msg_port_met_in5)
		self.set_msg_handler(self.msg_port_met_in5, self.met_in5)

		self.msg_port_met_in6 = pmt.intern('met in6')
		self.message_port_register_in(self.msg_port_met_in6)
		self.set_msg_handler(self.msg_port_met_in6, self.met_in6)

		self.msg_port_met_in7 = pmt.intern('met in7')
		self.message_port_register_in(self.msg_port_met_in7)
		self.set_msg_handler(self.msg_port_met_in7, self.met_in7)

		# Output ports
		self.msg_port_ctrl_out = pmt.intern('ctrl out')
		self.message_port_register_out(self.msg_port_ctrl_out)
		self.msg_port_broad_out = pmt.intern('broad out')
		self.message_port_register_out(self.msg_port_broad_out)
		self.msg_port_metrics_out = pmt.intern('metrics out')
		self.message_port_register_out(self.msg_port_metrics_out)

		self.start_block()
	# }}} __init__()

	# Aggregator
	def aggr(self, aggr, list): # {{{
		array = np.array(list)
		if len(array) == 0:
			met = None
		elif aggr == 0:
			met = array.sum()
		elif aggr == 1:
			#met = array.mean()
			met = array.sum()/(self.dec_gran/self.metrics_gran) # avg summation based on expected # of samples
		elif aggr == 2: 
			met = array.max()
		elif aggr == 3:
			met = array.min()
		elif aggr == 4:
			met = array.var()

		return met
	# }}} aggr()

	# This gets active MAC protocol on the network from sensor block
	def act_prot_in(self, msg): # {{{
		if self.coord == False: # Coord already knows the current MAC protocol
			portid = pmt.to_long(msg)

			msg = "portid" + str(portid)
			self.message_port_pub(self.msg_port_ctrl_out, pmt.string_to_symbol(msg))
			if portid == 0:
				print "Active protocol: CSMA/CA"
			elif portid == 1:
				print "Active protocol: TDMA"
	# }}} act_prot_in()

	def met_in0(self, msg):
		self.met0.append(pmt.to_float(msg))

	def met_in1(self, msg):
		self.met1.append(pmt.to_float(msg))

	def met_in2(self, msg):
		self.met2.append(pmt.to_float(msg))

	def met_in3(self, msg):
		self.met3.append(pmt.to_float(msg))

	def met_in4(self, msg):
		self.met4.append(pmt.to_float(msg))

	def met_in5(self, msg):
		self.met5.append(pmt.to_float(msg))

	def met_in6(self, msg):
		self.met6.append(pmt.to_float(msg))

	def met_in7(self, msg):
		self.met7.append(pmt.to_float(msg))

	# Init threads according to operation mode (Coord | Normal)
	def start_block(self):
		if self.coord:
			thread.start_new_thread(self.coord_loop, ('thread 1', 1))
			thread.start_new_thread(self.broadcast_prot, ('thread 2', 2))
		else:
			thread.start_new_thread(self.normal_loop, ('thread 3', 3))
		return

	# Machine Learning model
	def get_ml_model(self, mod=0): # {{{
		model = {
			0: {"model": nnet(max_iter=10000, hidden_layer_sizes=(20, ), solver="sgd", learning_rate_init=0.01), "name": "Neural Networks"}
		}

		print "ML algorithm = {}".format(model[mod]["name"])

		return model[mod]["model"]
	# }}} get_ml_model()

	# Feature-scaling
	def feature_scaling(self, X, num, den): # {{{
		_X = cp.deepcopy(X)
		for col in range(0, np.size(X, 1)):
			_X[:, col] = (_X[:, col] - num[col])/den[col]
		return _X
	# }}} feature_scaling()

	# Train model based on training set
	def train(self): # {{{
		data = np.loadtxt(self.train_file, delimiter=";") * 1.
		np.random.shuffle(data)

		print data.shape

		Y_csma = data[np.where(data[:, 0] == 0.0), 1]
		Y_csma = Y_csma.reshape(np.size(Y_csma, 1))
		Y_tdma = data[np.where(data[:, 0] == 1.0), 1]
		Y_tdma = Y_tdma.reshape(np.size(Y_tdma, 1))

		Y = {"csma": Y_csma, "tdma": Y_tdma}

		del_cols = np.array([1, 2, 3, 4, 7])
		data = np.delete(data, del_cols, axis=1)

		X = {
			"csma": data[np.where(data[:, 0] == 0.0), 1:][0],
			"tdma": data[np.where(data[:, 0] == 1.0), 1:][0]
		}

		stats = {
			"csma": {"num": np.mean(X["csma"], axis=0), "den": np.mean(X["csma"], axis=0)},
			"tdma": {"num": np.mean(X["tdma"], axis=0), "den": np.mean(X["tdma"], axis=0)}
		}

		X["csma"] = self.feature_scaling(X["csma"], stats["csma"]["num"], stats["csma"]["den"])
		X["tdma"] = self.feature_scaling(X["tdma"], stats["tdma"]["num"], stats["tdma"]["den"])

		csma_reg = self.get_ml_model(self.ml_alg)
		tdma_reg = self.get_ml_model(self.ml_alg)

		print X["csma"].shape, Y["csma"].shape

		csma_reg.fit(X["csma"], Y["csma"])
		tdma_reg.fit(X["tdma"], Y["tdma"])

		csma_reg.set_params(learning_rate_init=0.5)
		tdma_reg.set_params(learning_rate_init=0.5)

		return csma_reg, tdma_reg, stats
	# }}} train()

	def partial_fit(self, reg, batch, stats, prot): # {{{
		batch["y"] = np.delete(batch["y"], 0, axis=0) # -1
		batch["x"] = np.delete(batch["x"], 0, axis=0) # -1

		batch["x"] = self.feature_scaling(batch["x"], stats[prot]["num"], stats[prot]["den"])

		reg.partial_fit(batch["x"], batch["y"])

		return reg
	# }}} partial_fit()

	# Coordinator selects the MAC protocol to use in the network
	def coord_loop(self, name, id): # {{{
		global portid
		portid = 0

		f = open(self.backlog_file, "w", 0)
		f1 = open(self.backlog_file + "_parsed", "w", 0) # interpkt, snr, non and aggregations
		print "Decision block as Coordinator"

		csma_reg, tdma_reg, stats = self.train()

		# TODO: Online vs Offline learning
		# By now, I'm assuming only Online Regression

		time.sleep(3)
		sslc = 0 # Steps Since Last Change

		csma_batch = {"y": np.array([-1]), "x": np.array([[-1, -1, -1]])}
		tdma_batch = {"y": np.array([-1]), "x": np.array([[-1, -1, -1]])}

		while True: # {{{
			# Handling avg aggregation
			self.met4_max = self.aggr(2, self.met4)
			self.met4_min = self.aggr(3, self.met4)
			self.met4_std = self.aggr(4, self.met4)

			self.met5_max = self.aggr(2, self.met5)
			self.met5_min = self.aggr(3, self.met5)
			self.met5_std = self.aggr(4, self.met5)

			self.met0 = self.aggr(self.aggr0, self.met0)
			self.met1 = self.aggr(self.aggr1, self.met1)
			self.met2 = self.aggr(self.aggr2, self.met2)
			self.met3 = self.aggr(self.aggr3, self.met3)
			self.met4 = self.aggr(self.aggr4, self.met4)
			self.met5 = self.aggr(self.aggr5, self.met5)
			self.met6 = self.aggr(self.aggr6, self.met6)
			self.met7 = self.aggr(self.aggr7, self.met7)

			## {{{
			data = np.array([portid, self.met0, self.met1, self.met2, self.met3,\
					self.met4, self.met5, self.met6, self.met7])
			data = data.reshape((1, np.size(data)))
			
			if True not in [d is None for d in data[0]]:

				pred_prot = -1

				if sslc > 0:
					# prot;thr;lat;jit;rnp;interpkt;snr;cont;non
					#f.write("{};{};{};{};{};{};{};{};{}\n".format(\
					#	portid, self.met0, self.met1, self.met2, self.met3,\
					#	self.met4, self.met5, self.met6, self.met7))
					f.write("{};{};{};{};{};{};{};{};{};{};{};{};{};{};{}\n".format( \
						portid, self.met0, self.met1, self.met2, self.met3, \
						self.met4, self.met4_min, self.met4_max, self.met4_std, \
						self.met5, self.met5_min, self.met5_max, self.met5_std, \
						self.met6, self.met7))

					f1.write("{};{};{};{};{};{};{};{};{};{}\n".format(
						portid,
						self.met4, self.met4_min, self.met4_max, self.met4_std,
						self.met5, self.met5_min, self.met5_max, self.met5_std,
						self.met7
					))

					_y = data[:, 0]
					del_cols = np.array([0, 1, 2, 3, 4, 7]) # only usefull metrics remain
					_x = np.delete(data, del_cols, axis=1)

					if _y == 0.0:
						csma_batch["y"] = np.r_[csma_batch["y"], _y]

						print "csma_batch.shape = {}, _x.shape = {}".format(csma_batch["x"].shape, _x.shape)

						csma_batch["x"] = np.r_[csma_batch["x"], _x]

						if np.size(csma_batch["y"]) >= 4:
							print "Partial fit of CSMA regressor"
							
							csma_reg = self.partial_fit(csma_reg, csma_batch, stats, "csma")

							csma_batch = {"y": np.array([-1]), "x": np.array([[-1, -1, -1]])}

					elif _y == 1.0:
						tdma_batch["y"] = np.r_[tdma_batch["y"], _y]
						tdma_batch["x"] = np.r_[tdma_batch["x"], _x]
						
						if np.size(tdma_batch["y"]) >= 4:
							print "Partial fit of TDMA regressor"
							
							tdma_reg = self.partial_fit(tdma_reg, tdma_batch, stats, "tdma")

							tdma_batch = {"y": np.array([-1]), "x": np.array([[-1, -1, -1]])}
					
					# Prediction {{{					
					_x_csma = self.feature_scaling(_x, stats["csma"]["num"], stats["csma"]["den"])
					_x_tdma = self.feature_scaling(_x, stats["tdma"]["num"], stats["tdma"]["den"])

					pred_csma = csma_reg.predict(_x_csma)
					pred_tdma = tdma_reg.predict(_x_tdma)

					print "pred_csma = {}, pred_tdma = {}".format(
						round(pred_csma, 2), round(pred_tdma, 2)
					)

					if pred_csma > pred_tdma:
						pred_prot = 0
					else:
						pred_prot = 1
					# }}} Prediction

				else:
					pred_prot = portid

				sslc = sslc + 1

				if pred_prot != portid:
					print "Protocol change from {} to {}".format(portid, pred_prot)

					portid = pred_prot
					sslc = 0

				else:
					print "Protocol remains the same"
			## }}}

			if portid == 0:
				print "Active protocol: CSMA/CA"
			elif portid == 1:
				print "Active protocol: TDMA"

			# Broadcast MAC prot {{{
			self.message_port_pub(self.msg_port_ctrl_out, pmt.string_to_symbol('portid' + str(portid)))
			# }}}

			# Reseting metric counters {{{
			self.met0 = []
			self.met1 = []
			self.met2 = []
			self.met3 = []
			self.met4 = []
			self.met5 = []
			self.met6 = []
			self.met7 = []
			# }}}

			time.sleep(self.dec_gran)

		# }}} while
	# }}} coord_loop()

	# Coordinator broadcasts the MAC protocol in use
	def broadcast_prot(self, name, id): # {{{
		global portid

		print "Broadcasting thread"
		while True:
			msg = "act_prot:" + str(portid)
			self.message_port_pub(self.msg_port_broad_out, pmt.string_to_symbol(msg))
			time.sleep(self.broad_gran)
	# }}} broadcast_prot()

	# Useful at the beginning, in order to inform normal node to use no MAC protocol (portid = 200, none)
	def normal_loop(self, name, id): # {{{
		global portid
		portid = 200

		print "Decision block as Normal node"
		# Sets no MAC protocol at the beginning (portid = 200, none)
		self.message_port_pub(self.msg_port_ctrl_out, pmt.string_to_symbol('portid' + str(portid)))

		while True:
			time.sleep(self.metrics_gran)
			msg = "send_metrics"
			self.message_port_pub(self.msg_port_metrics_out, pmt.string_to_symbol(msg))
	# }}} normal_loop()