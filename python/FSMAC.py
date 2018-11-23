#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

class FSMAC:
	def __init__(self, prot = 0):
		self.prot = prot
		self.act_protocol = prot + 1

		return

	def decision(self, non, lat):
		# non: number of nodes
		# lat: latency
		csma = float(self.calculate_csma_adaptability(non, lat/2.))
		tdma = float(self.calculate_tdma_adaptability(non, lat/2.))

		logging.info("Prot = {}".format("CSMA" if self.prot == 0 else "TDMA"))
		logging.info("non = {}, lat = {}".format(non, lat))
		logging.info("Adaptability: CSMA = {}, TDMA = {}".format(csma, tdma))
		logging.info("\n")

		# 0: CSMA
		# 1: TDMA
		if csma == tdma:
			prot = self.pro
		else:
			prot = 0 if csma > tdma else 1
		
		self.prot = prot
		self.act_protocol = prot + 1

		return prot

####################################
# Code below is from FSMA project
# Refer to https://github.com/jeffRayneres/FS-MAC for further information
####################################


	def calculate_tdma_adaptability(self, sens1_value, sens2_value):
		#if senders is higth AND data is higth then TDMA adaptability is hight
		#if senders is low AND data is higth then TDMA adaptability is low
		tdma_low_pert_decimals = [0,10,20,30,40,50,60]
		tdma_hight_pert_decimals = [40,50,60,70,80,90,100]

		csma_low_pert_decimals = [0,10,20,30,40,50,60]
		csma_hight_pert_decimals = [40,50,60,70,80,90,100]

		#======= FUZZYFICATION PHASE =======#
		senders_fuzy_pert = self.senders_function(sens1_value);
		data_fuzzy_pert = self.data_function(sens2_value);
		#===================================#

		numerator = 0
		denominator = 0

		value_hight_adapt = 0
		value_low_adapt = 0

		list_low_adapts = []
		list_hight_adapts = []

		#======= EVALUATION OF RULES =======#
		#if senders is higth AND data is higth then TDMA adaptability is hight
		#Intersection gets minimum between two values
		if senders_fuzy_pert[1] < data_fuzzy_pert[1]:
			list_hight_adapts.append(senders_fuzy_pert[1])
		else:
			list_hight_adapts.append(data_fuzzy_pert[1])

		#if senders is low AND data is higth then TDMA adaptability is low
		#Intersection gets minimum between two values
		if senders_fuzy_pert[0] < data_fuzzy_pert[1]:
			list_low_adapts.append(senders_fuzy_pert[0])
		else:
			list_low_adapts.append(data_fuzzy_pert[1])

		#if senders is higth AND data is low then TDMA adaptability is low
		#Intersection gets minimum between two values
		if senders_fuzy_pert[1] < data_fuzzy_pert[0]:
			list_low_adapts.append(senders_fuzy_pert[1])
		else:
			list_low_adapts.append(data_fuzzy_pert[0])

		#if senders is low AND data is low then TDMA adaptability is low
		#Intersection gets minimum between two values
		if senders_fuzy_pert[0] < data_fuzzy_pert[0]:
			list_low_adapts.append(senders_fuzy_pert[0])
		else:
			list_low_adapts.append(data_fuzzy_pert[0])

		list_low_adapts.sort(reverse=True)
		list_hight_adapts.sort(reverse=True)

		value_low_adapt = list_low_adapts[0]
		value_hight_adapt = list_hight_adapts[0]
		#===================================#

		#====== DEFUZZYFICATION PHASE ======#
		for i in tdma_hight_pert_decimals:
			numerator = numerator + i*value_hight_adapt

		for j in tdma_low_pert_decimals:
			numerator = numerator + j*value_low_adapt

		denominator = denominator + len(tdma_hight_pert_decimals)*value_hight_adapt
		denominator = denominator + len(tdma_low_pert_decimals)*value_low_adapt

		if denominator == 0:
			denominator = 1

		adaptability_degree = numerator/denominator
		#===================================#

		return adaptability_degree


	def calculate_csma_adaptability(self, sens1_value, sens2_value):
		#if senders is higth AND data is higth then CSMA adaptability is low
		#if senders is low AND data is higth then CSMA adaptability is higth
		tdma_low_pert_decimals = [0,10,20,30,40,50,60]
		tdma_hight_pert_decimals = [40,50,60,70,80,90,100]

		csma_low_pert_decimals = [0,10,20,30,40,50,60]
		csma_hight_pert_decimals = [40,50,60,70,80,90,100]

		#======= FUZZYFICATION PHASE =======#
		senders_fuzy_pert = self.senders_function(sens1_value)
		data_fuzzy_pert = self.data_function(sens2_value)
		#===================================#

		numerator = 0
		denominator = 0

		value_hight_adapt = 0
		value_low_adapt = 0

		list_low_adapts = []
		list_hight_adapts = []

		#======= EVALUATION OF RULES =======#
		#if senders is higth AND data is higth then CSMA adaptability is low
		#Intersection gets minimum between two values
		if senders_fuzy_pert[1] < data_fuzzy_pert[1]:
			list_low_adapts.append(senders_fuzy_pert[1])
		else:
			list_low_adapts.append(data_fuzzy_pert[1])

		#if senders is low AND data is higth then CSMA adaptability is higth
		#Intersection gets minimum between two values
		if senders_fuzy_pert[0] < data_fuzzy_pert[1]:
			list_hight_adapts.append(senders_fuzy_pert[0])
		else:
			list_hight_adapts.append(data_fuzzy_pert[1])
		#===================================#

		#if senders is hight AND data is low then CSMA adaptability is higth
		if senders_fuzy_pert[1] < data_fuzzy_pert[0]:
			list_hight_adapts.append(senders_fuzy_pert[1])
		else:
			list_hight_adapts.append(data_fuzzy_pert[0])

		#if senders is low AND data is low then CSMA adaptability is hight
		if senders_fuzy_pert[0] < data_fuzzy_pert[0]:
			list_hight_adapts.append(senders_fuzy_pert[0])
		else:
			list_hight_adapts.append(data_fuzzy_pert[0])


		list_hight_adapts.sort(reverse=True)
		list_low_adapts.sort(reverse=True)

		value_hight_adapt = list_hight_adapts[0]
		value_low_adapt = list_low_adapts[0]


		#====== DEFUZZYFICATION PHASE ======#
		for i in csma_hight_pert_decimals:
			numerator = numerator + i*value_hight_adapt

		for j in csma_low_pert_decimals:
			numerator = numerator + j*value_low_adapt

		denominator = denominator + len(csma_hight_pert_decimals)*value_hight_adapt
		denominator = denominator + len(csma_low_pert_decimals)*value_low_adapt

		if denominator == 0:
			denominator = 1

		adaptability_degree = numerator/denominator
		#===================================#

		return adaptability_degree

	
	def senders_function(self, x):
		low_pert = 0;
		hight_pert = 0;

	#---- BEGIN COMMENT HERE FOR EXPERIMENT 2 ---
		if x >= 0 and x <= 1:
			low_pert = 100
		elif x > 1 and x < 2:
			low_pert = -100*x  + 200
		else:
			low_pert = 0
		
		if x >= 0 and x <= 1:
			hight_pert = 0
		elif x > 1 and x < 2:
			hight_pert = 100*x - 100
		else:
			hight_pert = 100
	#---- END COMMENT HERE FOR EXPERIMENT 2 ---

	#---- BEGIN UNCOMMENT HERE FOR EXPERIMENT 2 ---
		#if x >= 0 and x <= 2:
		#	low_pert = 100
		#elif x > 2 and x < 3:
		#	low_pert = -100*x + 300
		#else:
		#	low_pert = 0
		#
		#if x >= 0 and x <= 2:
		#	hight_pert = 0
		#elif x > 2 and x < 3:
		#	hight_pert = 100*x - 200
		#else:
		#	hight_pert = 100
	#---- END UNCOMMENT HERE FOR EXPERIMENT 2 ---

		return [low_pert, hight_pert]

	def data_function(self, x):
		low_pert = 0;
		hight_pert = 0;
	
	#---- BEGIN COMMENT HERE FOR EXPERIMENT 2 ---
		if self.act_protocol == 1:
			if x >= 0 and x <= 20:
				low_pert = 100
			elif x > 20 and x < 40:
				low_pert = -5*x  + 200
			else:
				low_pert = 0
		
			if x >= 0 and x <= 20:
				hight_pert = 0
			elif x > 20 and x < 40:
				hight_pert = 5*x - 100
			else:
				hight_pert = 100
		
		elif self.act_protocol == 2:
			if x >= 0 and x <= 20:
				low_pert = 100
			elif x > 20 and x < 25:
				low_pert = -20*x  + 500
			else:
				low_pert = 0
		
			if x >= 0 and x <= 20:
				hight_pert = 0
			elif x > 20 and x < 25:
				hight_pert = 20*x - 400
			else:
				hight_pert = 100
	#---- END COMMENT HERE FOR EXPERIMENT 2 ---

	#---- BEGIN UNCOMMENT HERE FOR EXPERIMENT 2 ---
		#if self.act_protocol == 1:
		#	if x >= 0 and x <= 35:
		#		low_pert = 100
		#	elif x > 35 and x < 55:
		#		low_pert = -5*x  + 275
		#	else:
		#		low_pert = 0
		#
		#	if x >= 0 and x <= 35:
		#		hight_pert = 0
		#	elif x > 35 and x < 55:
		#		hight_pert = 5*x - 175
		#	else:
		#		hight_pert = 100
		#
		#elif self.act_protocol == 2:
		#	if x >= 0 and x <= 23:
		#		low_pert = 100
		#	elif x > 23 and x < 26:
		#		low_pert = -33.33334*x  + 866.6667
		#	else:
		#		low_pert = 0
		#
		#	if x >= 0 and x <= 23:
		#		hight_pert = 0
		#	elif x > 23 and x < 26:
		#		hight_pert = 33.33334*x - 766.6667
		#	else:
		#		hight_pert = 100
	#---- END UNCOMMENT HERE FOR EXPERIMENT 2 ---

		return [low_pert, hight_pert]