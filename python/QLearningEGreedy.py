#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import time
import logging

class QLearningEGreedy:

	def __init__(self, prot, learn_rate = 0.3, discount = 0.8, epsilon = 0.1):
		logging.info("QLearnging e-greedy")

		self.q_table	= np.zeros((2, 2))
		#self.q_table	= np.random.rand(2, 2) - 0.5
		self.discount   = discount
		self.learn_rate = learn_rate
		self.reward	    = 0.

		self.epsilon    = epsilon

		self.t		    = 1

		seed = int(time.time())
		np.random.seed(seed)

		_ = self.decision(prot)

		return
		
	def decision(self, prot, keep = False, force_switch = False):
		self.state = prot

		#epsilon = 1. / (np.log2(self.t + 1.))
		epsilon = self.epsilon
		self.t = self.t + 1

		if force_switch == True:
			action = 0 if prot == 1 else 1

		elif keep == False:
			if self.q_table[self.state, 0] == self.q_table[self.state, 1] or \
					np.random.rand() < epsilon:
				action = np.random.randint(2)
				logging.info("Random choice = {}".format(action))
			else:
				action = np.argmax(self.q_table[self.state, :])

		else:
			action = prot
		
		self.action = action
		self.state_new = action
		
		return action
	
	def update_qtable(self, reward, dt = 0):
		self.q_table[self.state, self.action] = (1. - self.learn_rate) * self.q_table[self.state, self.action] + \
						self.learn_rate * (reward + self.discount * np.max(self.q_table[self.state_new, :]))

		logging.info("Reward = {}".format(reward))
		logging.info("QTable = \n{}".format(self.q_table))
		
		return

	def reset_qtable(self):
		self.q_table = np.random.rand(2, 2) - 0.5

		return
