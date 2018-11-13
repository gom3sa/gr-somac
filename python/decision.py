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
import logging
import copy as cp
from QLearningEGreedy import QLearningEGreedy as egreedy
from QLearningBoltzmann import QLearningBoltzmann as boltz

portid = 200 # Initially no MAC protocol is used. The normal node waits for coordinator's message.
threshold = 0.1 # Threshold for switching MAC protocol

class decision(gr.basic_block):
	"""
	MAC protocols:
		CSMA/CA:	portid = 0
		TDMA:		portid = 1
	"""
	def __init__(self, coord, dec_gran, broad_gran, metrics_gran, exploration, metric, aggr, minmax, backlog_file): # {{{

		gr.basic_block.__init__(self, name="decision", in_sig=None, out_sig=None)

		self.coord        = coord # Is coordinator? 
		self.dec_gran     = dec_gran # Granularity of decision
		self.broad_gran   = broad_gran
		self.metrics_gran = metrics_gran
		self.backlog_file = backlog_file

		self.met0, self.met1, self.met2, self.met3, self.met4, \
			self.met5, self.met6, self.met7, self.met8, self.met9 = [[] for _ in range(10)]    

		self.exploration = exploration
		self.metric      = metric
		self.aggregation = aggr
		self.minmax      = minmax # target metric should be minimized ou maximized?

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

		self.msg_port_met_in8 = pmt.intern('met in8')
		self.message_port_register_in(self.msg_port_met_in8)
		self.set_msg_handler(self.msg_port_met_in8, self.met_in8)

		self.msg_port_met_in9 = pmt.intern('met in9')
		self.message_port_register_in(self.msg_port_met_in9)
		self.set_msg_handler(self.msg_port_met_in9, self.met_in9)

		# Output ports
		self.msg_port_ctrl_out    = pmt.intern('ctrl out')
		self.message_port_register_out(self.msg_port_ctrl_out)
		self.msg_port_broad_out   = pmt.intern('broad out')
		self.message_port_register_out(self.msg_port_broad_out)
		self.msg_port_metrics_out = pmt.intern('metrics out')
		self.message_port_register_out(self.msg_port_metrics_out)

		logging.basicConfig(filename="/tmp/out.log", level = logging.INFO)

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
		elif aggr == 5:
			met = array.shape[0]

		return met
	# }}} aggr()

	# This gets active MAC protocol on the network from sensor block
	def act_prot_in(self, msg): # {{{
		if self.coord == False: # Coord already knows the current MAC protocol
			portid = pmt.to_long(msg)

			msg = "portid" + str(portid)
			self.message_port_pub(self.msg_port_ctrl_out, pmt.string_to_symbol(msg))
			if portid == 0:
				logging.info("Active protocol: CSMA/CA")
			elif portid == 1:
				logging.info("Active protocol: TDMA")
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

	def met_in8(self, msg):
		self.met8.append(pmt.to_float(msg))

	def met_in9(self, msg):
		self.met9.append(pmt.to_float(msg))

	# Init threads according to operation mode (Coord | Normal)
	def start_block(self): # {{{
		if self.coord:
			thread.start_new_thread(self.coord_loop, ('thread 1', 1))
			thread.start_new_thread(self.broadcast_prot, ('thread 2', 2))
		else:
			thread.start_new_thread(self.normal_loop, ('thread 3', 3))
		return
	# }}} start_block()

	def calc_reward(self, curr, prev): # {{{
		if curr > prev:
			reward = curr / prev - 1. if prev > 0. else 0.
		else:
			reward = - (prev / curr - 1.) if curr > 0. else 0.
		if reward > 1. or reward < -1:
			reward = 1 if reward > 1 else -1

		if self.minmax == 0:	# min
			return reward * -5.
		elif self.minmax == 1:	# max
			return reward * 5.
	# }}}

	# Coordinator selects the MAC protocol to use in the network
	def coord_loop(self, name, id): # {{{
		global portid

		#portid = 1
		# Random init
		portid = np.random.choice([0, 1], p = [0.5, 0.5])

		##### MODE #####
		f_mode = open("/tmp/prot.txt", "r")
		mode = int(f_mode.readline().strip("\n"))

		if mode == 0 or mode == 1:
			portid = mode
		################

		reward = 0.
		prev_portid = portid

		# ML modules
		if mode == 2:
			somac = egreedy(portid)
		elif mode == 3:
			somac = boltz(prot = portid, learn_rate = 0.6, discount = 0.8, T = 0.5)
		
		# Detects whether or not a prot switch has just occured
		# _p: protocol, _pp: previous protocol
		is_transition = lambda _p, _pp: 1. if _p != _pp else 0.

		dt = -2 # delta time since last protocol switch
		t  = 0

		logging.info("Decision block as Coordinator")
		time.sleep(3)

		prev = -1
		prev_prev = -1

		target_metric = {}

		while True: # {{{
			# Handling avg aggregation
			# [sum, avg, max, min, var, count]
			self.met0_list = [self.aggr(i, self.met0) for i in range(6)]
			self.met1_list = [self.aggr(i, self.met1) for i in range(6)]
			self.met2_list = [self.aggr(i, self.met2) for i in range(6)]
			self.met3_list = [self.aggr(i, self.met3) for i in range(6)]
			self.met4_list = [self.aggr(i, self.met4) for i in range(6)]
			self.met5_list = [self.aggr(i, self.met5) for i in range(6)]
			self.met6_list = [self.aggr(i, self.met6) for i in range(6)]
			self.met7_list = [self.aggr(i, self.met7) for i in range(6)]
			self.met8_list = [self.aggr(i, self.met8) for i in range(6)]
			self.met9_list = [self.aggr(i, self.met9) for i in range(6)]

			metrics = np.array([self.met0_list, self.met1_list, self.met2_list,	\
						self.met3_list, self.met4_list, self.met5_list,	\
						self.met6_list, self.met7_list, self.met8_list, \
						self.met9_list])

			logging.info("Active protocol: {}".format("CSMA" if portid == 0 else "TDMA"))

			if np.any(np.equal(metrics, None)) == False: # {{{
				log_dict = {}
				if t > 0:
					log_dict = np.load(self.backlog_file).item()

				log_dict[t] = {	"prot": portid, "metrics": metrics,
						"transition": is_transition(portid, prev_portid),
						"dt": dt }

				dt = dt + 1
				prev_portid = portid

				np.save(self.backlog_file, log_dict)

				target_metric[t] = log_dict[t]["metrics"][self.metric, self.aggregation]
				
				logging.info("Target metric = {}".format(target_metric[t]))

				# TODO: Decision {{{
				# Guarantees two decision are not done in a row
				# This is the mode code for SOMAC
				if (mode == 2 or mode == 3) and dt > 1: 

					if dt == 2:
						reward = self.calc_reward(target_metric[t], target_metric[t - 2])
					elif dt == 3:
						reward = self.calc_reward(target_metric[t], target_metric[t-3])
					else:
						reward = self.calc_reward(target_metric[t], target_metric[t-1])

						if reward >= 0:
							reward = 0
						else:
							reward = reward

					logging.info("dt = {}".format(dt))
					somac.update_qtable(reward, dt)

					if dt == 2 and reward > 0:
						decision = somac.decision(portid, keep = True)
					elif dt == 2 and reward < 0:
						decision = somac.decision(portid, force_switch = True)
					else:
						decision = somac.decision(portid, keep = False)

					logging.info("Decision: {}".format(decision))

					if portid != decision: 
						portid = decision
						dt = 0
				# }}}
				else:
					logging.info("No decision: protocol was switched last time")

				t = t + 1
			else:
				logging.info("Metrics contain None")
			## }}}

			# Broadcast MAC prot {{{
			self.message_port_pub(self.msg_port_ctrl_out, pmt.string_to_symbol('portid' + str(portid)))
			# }}}

			# Reseting metric counters {{{
			self.met0, self.met1, self.met2, self.met3, self.met4, \
				self.met5, self.met6, self.met7, self.met8, self.met9 = [[] for _ in range(10)]
			# }}

			logging.info("-----")
			time.sleep(self.dec_gran)
		# }}} while
	# }}} coord_loop()

	# Coordinator broadcasts the MAC protocol in use
	def broadcast_prot(self, name, id): # {{{
		global portid

		while True:
			msg = "act_prot:" + str(portid)
			self.message_port_pub(self.msg_port_broad_out, pmt.string_to_symbol(msg))
			time.sleep(self.broad_gran)
	# }}} broadcast_prot()

	# Useful at the beginning, in order to inform normal node to use no MAC protocol (portid = 200, none)
	def normal_loop(self, name, id): # {{{
		global portid
		portid = 200

		logging.info("Decision block as Normal node")

		# Sets no MAC protocol at the beginning (portid = 200, none)
		self.message_port_pub(self.msg_port_ctrl_out, pmt.string_to_symbol('portid' + str(portid)))

		while True:
			time.sleep(self.metrics_gran)
			msg = "send_metrics"
			self.message_port_pub(self.msg_port_metrics_out, pmt.string_to_symbol(msg))
	# }}} normal_loop()

