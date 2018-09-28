#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import time
import logging

class QLearning:

	def __init__(self, prot):
		logging.info("QLearngin e-greedy")

		self.q_table	= np.zeros((2, 2))
		#self.q_table	= np.random.rand(2, 2) - 0.5
		self.discount   = 0.8
		self.learn_rate = 0.3
		self.reward	    = 0.

		self.t		    = 1

		seed = int(time.time())
		np.random.seed(seed)

		_ = self.decision(prot)

		return
		
	def decision(self, prot):
		self.state = prot

		epsilon = 1. / (np.log2(self.t + 1.))
		self.t = self.t + 1
		
		if self.q_table[self.state, 0] == self.q_table[self.state, 1] or \
				np.random.rand() < epsilon:
			action = np.random.randint(2)
			logging.info("Random choice = {}".format(action))
		else:
			action = np.argmax(self.q_table[self.state, :])
		
		self.action = action
		self.state_new = action
		
		return action
	
	def update_qtable(self, reward):
		self.q_table[self.state, self.action] = (1. - self.learn_rate) * self.q_table[self.state, self.action] + \
						self.learn_rate * (reward + self.discount * np.max(self.q_table[self.state_new, :]))

		logging.info("Reward = {}".format(reward))
		logging.info("QTable = \n{}".format(self.q_table))
		
		return

	def reset_qtable(self):
		self.q_table = np.random.rand(2, 2) - 0.5

		return
