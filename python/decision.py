#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2018 André Gomes, UFMG - <andre.gomes@dcc.ufmg.br>.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy
from gnuradio import gr
import pmt
import time
import thread
import numpy as np

portid = 200; # Initially no MAC protocol is used. The normal node waits for coordinator's message.

class decision(gr.basic_block):
	"""
	MAC protocols:
		CSMA/CA:	portid = 0
		TDMA:		portid = 1
	"""
	def __init__(self, coord, dec_gran, broad_gran, metrics_gran, backlog_file, aggr0, \
			aggr1, aggr2, aggr3, aggr4, aggr5, aggr6, aggr7):
		gr.basic_block.__init__(self, name="decision", in_sig=None, out_sig=None)

		self.coord = coord; # Is coordinator? 
		self.dec_gran = dec_gran; # Granularity of decision
		self.broad_gran = broad_gran;
		self.metrics_gran = metrics_gran;
		self.backlog_file = backlog_file;

		self.met0 = [];
		self.met1 = [];
		self.met2 = [];
		self.met3 = [];
		self.met4 = [];
		self.met5 = [];
		self.met6 = [];
		self.met7 = [];

		self.aggr0 = aggr0;
		self.aggr1 = aggr1;
		self.aggr2 = aggr2;
		self.aggr3 = aggr3;
		self.aggr4 = aggr4;
		self.aggr5 = aggr5;
		self.aggr6 = aggr6;
		self.aggr7 = aggr7;

		# Input ports
		self.msg_port_act_prot_in = pmt.intern('act prot in');
		self.message_port_register_in(self.msg_port_act_prot_in);
		self.set_msg_handler(self.msg_port_act_prot_in, self.act_prot_in);

		self.msg_port_met_in0 = pmt.intern('met in0');
		self.message_port_register_in(self.msg_port_met_in0);
		self.set_msg_handler(self.msg_port_met_in0, self.met_in0);

		self.msg_port_met_in1 = pmt.intern('met in1');
		self.message_port_register_in(self.msg_port_met_in1);
		self.set_msg_handler(self.msg_port_met_in1, self.met_in1);

		self.msg_port_met_in2 = pmt.intern('met in2');
		self.message_port_register_in(self.msg_port_met_in2);
		self.set_msg_handler(self.msg_port_met_in2, self.met_in2);

		self.msg_port_met_in3 = pmt.intern('met in3');
		self.message_port_register_in(self.msg_port_met_in3);
		self.set_msg_handler(self.msg_port_met_in3, self.met_in3);

		self.msg_port_met_in4 = pmt.intern('met in4');
		self.message_port_register_in(self.msg_port_met_in4);
		self.set_msg_handler(self.msg_port_met_in4, self.met_in4);

		self.msg_port_met_in5 = pmt.intern('met in5');
		self.message_port_register_in(self.msg_port_met_in5);
		self.set_msg_handler(self.msg_port_met_in5, self.met_in5);

		self.msg_port_met_in6 = pmt.intern('met in6');
		self.message_port_register_in(self.msg_port_met_in6);
		self.set_msg_handler(self.msg_port_met_in6, self.met_in6);

		self.msg_port_met_in7 = pmt.intern('met in7');
		self.message_port_register_in(self.msg_port_met_in7);
		self.set_msg_handler(self.msg_port_met_in7, self.met_in7);

		# Output ports
		self.msg_port_ctrl_out = pmt.intern('ctrl out');
		self.message_port_register_out(self.msg_port_ctrl_out);
		self.msg_port_broad_out = pmt.intern('broad out');
		self.message_port_register_out(self.msg_port_broad_out);
		self.msg_port_metrics_out = pmt.intern('metrics out');
		self.message_port_register_out(self.msg_port_metrics_out);

		self.start_block();

	# Aggregator
	def aggr(self, aggr, list):
		array = np.array(list);
		if len(array) == 0:
			met = None;
		elif aggr == 0:
			met = array.sum();
		elif aggr == 1:
			#met = array.mean();
			met = array.sum()/(self.dec_gran/self.metrics_gran); # avg summation based on expected # of samples
		elif aggr == 2: 
			met = array.max();
		elif aggr == 3:
			met == array.min();

		return met;

	# This gets active MAC protocol on the network from sensor block
	def act_prot_in(self, msg):
		if self.coord == False: # Coord already knows the current MAC protocol
			portid = pmt.to_long(msg);

			msg = "portid" + str(portid);
			self.message_port_pub(self.msg_port_ctrl_out, pmt.string_to_symbol(msg));
			if portid == 0:
				print "Active protocol: CSMA/CA"
			elif portid == 1:
				print "Active protocol: TDMA"

	def met_in0(self, msg):
		self.met0.append(pmt.to_float(msg));

	def met_in1(self, msg):
		self.met1.append(pmt.to_float(msg));

	def met_in2(self, msg):
		self.met2.append(pmt.to_float(msg));

	def met_in3(self, msg):
		self.met3.append(pmt.to_float(msg));

	def met_in4(self, msg):
		self.met4.append(pmt.to_float(msg));

	def met_in5(self, msg):
		self.met5.append(pmt.to_float(msg));

	def met_in6(self, msg):
		self.met6.append(pmt.to_float(msg));

	def met_in7(self, msg):
		self.met7.append(pmt.to_float(msg));

	# Init threads according to operation mode (Coord | Normal)
	def start_block(self):
		if self.coord:
			thread.start_new_thread(self.coord_loop, ('thread 1', 1));
			thread.start_new_thread(self.broadcast_prot, ('thread 2', 2));
		else:
			thread.start_new_thread(self.normal_loop, ('thread 3', 3));

	# Coordinator selects the MAC protocol to use in the network
	def coord_loop(self, name, id):
		global portid;
		portid = 0;

		f = open(self.backlog_file, "w", 0);
		print "Decision block as Coordinator"

		time.sleep(3);
		while True:
			# Handling avg aggregation
			self.met0 = self.aggr(self.aggr0, self.met0);
			self.met1 = self.aggr(self.aggr1, self.met1);
			self.met2 = self.aggr(self.aggr2, self.met2);
			self.met3 = self.aggr(self.aggr3, self.met3);
			self.met4 = self.aggr(self.aggr4, self.met4);
			self.met5 = self.aggr(self.aggr5, self.met5);
			self.met6 = self.aggr(self.aggr6, self.met6);
			self.met7 = self.aggr(self.aggr6, self.met7);

			# Write metrics to backlog file
			string ="prot = " + str(portid) +  ", thr = " + str(self.met0) + ", lat = " + str(self.met1) + \
				", jit = " + str(self.met2) + ", rnp = " + str(self.met3) + ", interpkt = " + \
				str(self.met4) + ", snr = " + str(self.met5) + ", cont = " + str(self.met6) + \
				", non = " + str(self.met7);
			f.write(string + "\n");
			print string;

			## START: set portid
			portid = portid + 1;
			if portid > 1:
				portid = 0;
			portid = 0;
			## END: set portid

			if portid == 0:
				print "Active protocol: CSMA/CA"
			elif portid == 1:
				print "Active protocol: TDMA"

			## START: select MAC protocol according to portid
			self.message_port_pub(self.msg_port_ctrl_out, pmt.string_to_symbol('portid' + str(portid)));
			## END: select MAC protocol according to portid

			# Reseting metric counters
			self.met0 = [];
			self.met1 = [];
			self.met2 = [];
			self.met3 = [];
			self.met4 = [];
			self.met5 = [];
			self.met6 = [];
			self.met7 = [];

			time.sleep(self.dec_gran);

	# Coordinator broadcasts the MAC protocol in use
	def broadcast_prot(self, name, id): 
		global portid;

		print "Broadcasting thread"
		while True:
			msg = "act_prot:" + str(portid);
			print msg
			self.message_port_pub(self.msg_port_broad_out, pmt.string_to_symbol(msg));
			time.sleep(self.broad_gran);

	# Useful at the beginning, in order to inform normal node to use no MAC protocol (portid = 200, none)
	def normal_loop(self, name, id):
		global portid;
		portid = 200;

		print "Decision block as Normal node"
		self.message_port_pub(self.msg_port_ctrl_out, pmt.string_to_symbol('portid' + str(portid))); # Sets no MAC protocol at the beginning (portid = 200, none)

		while True:
			time.sleep(self.metrics_gran);
			msg = "send_metrics";
			self.message_port_pub(self.msg_port_metrics_out, pmt.string_to_symbol(msg));
