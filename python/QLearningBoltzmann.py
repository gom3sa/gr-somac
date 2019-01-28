#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import time
import logging

class QLearningBoltzmann:

	def __init__(self, prot, learn_rate = 0.3, discount = 0.8, T = 1.0):
		self.q_table   = np.zeros((2, 2))
		
		self.prob_table = np.zeros((2, 2)) + 0.5
		self.discount   = discount
		self.learn_rate = learn_rate
		self.reward     = 0.

		self.T          = T

		seed = int(time.time())
		np.random.seed(seed)

		_ = self.decision(prot, keep = True)
		
		logging.info("QLearnging Boltzmann")
		logging.info("T = {}, learn_rate = {}, discount factor = {}".format(self.T, self.learn_rate, self.discount))

		return
		
	def decision(self, prot, keep = False, force_switch = False):
		self.state = prot

		if force_switch == True:
			action = 0 if prot == 1 else 1
		elif keep == False:
			action = np.random.choice(
					np.array([0, 1]),
					p = self.prob_table[self.state]
				)
		else:
			action = prot

		logging.info("Choice = {}".format(action))
		
		self.action = action
		self.state_new = action
		
		return action

	def update_qtable(self, reward, dt):
		self.q_table[self.state, self.action] = (1. - self.learn_rate) * self.q_table[self.state, self.action] + \
						self.learn_rate * (reward + self.discount * np.max(self.q_table[self.state_new, :]))

		T = self.T
		num = np.exp(self.q_table / T)

		sum_cols = np.sum(num, 1)
		for row in range(num.shape[0]):
			num[row, :] = num[row, :] / sum_cols[row]

		self.prob_table = num

		logging.info("Temperature = {}".format(T))
		logging.info("Reward = {}".format(reward))
		logging.info("QTable = \n{}".format(self.q_table))
		logging.info("Prob Table = \n{}".format(self.prob_table))

		return

	def reset_qtable(self):
		self.q_table   = np.zeros((2, 2))
		self.prob_table = np.zeros((2, 2)) + 0.5

		return
