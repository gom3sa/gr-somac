#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import time
import logging

class QLearningBoltzmann:

	def __init__(self, prot):
		logging.info("QLearngin with Boltzmann equation")
		#self.q_table   = np.zeros((2, 2))
		
		self.q_table	= np.random.rand(2, 2) - 0.5
		self.prob_table = np.zeros((2, 2)) + 0.5
		self.T		    = 1
		self.discount   = 0.8
		self.learn_rate = 0.3
		self.reward     = 0.

		seed = int(time.time())
		np.random.seed(seed)

		_ = self.decision(prot)

		return
		
	def decision(self, prot):
		self.state = prot

		action = np.random.choice(
				np.array([0, 1]),
				p = self.prob_table[self.state]
			)

		logging.info("Choice = {}".format(action))
		
		self.action = action
		self.state_new = action
		
		return action
	
	def update_qtable(self, reward):
		self.q_table[self.state, self.action] = (1. - self.learn_rate) * self.q_table[self.state, self.action] + \
						self.learn_rate * (reward + self.discount * np.max(self.q_table[self.state_new, :]))

		num = np.exp(self.prob_table / self.T)

		sum_cols = np.sum(num, 1)
		for row in range(num.shape[0]):
			num[row, :] = np[row, :] / sum_cols[row]

		self.prob_table = num

		logging.info("Reward = {}".format(reward))
		logging.info("QTable = \n{}".format(self.q_table))
		logging.info("Prob Table = \n{}".format(self.prob_table))

		return

	def reset_qtable(self):
		self.q_table = np.random.rand(2, 2) - 0.5

		return
