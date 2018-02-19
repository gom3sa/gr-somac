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

portid = -1; # Initially no MAC protocol is used. The normal node waits for coordinator's message.

class decision(gr.basic_block):
	"""
	MAC protocols:
		CSMA/CA:	portid = 0
		TDMA:		portid = 1
	"""
	def __init__(self, coord, dec_gran, broad_gran, metrics_gran, backlog_file, aggr0, aggr1, aggr2, aggr3, aggr4, aggr5):
		gr.basic_block.__init__(self, name="decision", in_sig=None, out_sig=None)

		self.coord = coord; # Is coordinator? 
		self.dec_gran = dec_gran; # Granularity of decision
		self.broad_gran = broad_gran;
		self.metrics_gran = metrics_gran;
		self.backlog_file = backlog_file;

		self.met0 = self.met1 = self.met2 = self.met3 = self.met4 = self.met5 = 0;
		self.count0 = self.count1 = self.count2 = self.count3 = self.count4 = self.count5 = 0;

		self.aggr0 = aggr0;
		self.aggr1 = aggr1;
		self.aggr2 = aggr2;
		self.aggr3 = aggr3;
		self.aggr4 = aggr4;
		self.aggr5 = aggr5;

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

		# Output ports
		self.msg_port_ctrl_out = pmt.intern('ctrl out');
		self.message_port_register_out(self.msg_port_ctrl_out);
		self.msg_port_broad_out = pmt.intern('broad out');
		self.message_port_register_out(self.msg_port_broad_out);
		self.msg_port_metrics_out = pmt.intern('metrics out');
		self.message_port_register_out(self.msg_port_metrics_out);

		self.start_block();

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
		met = pmt.to_float(msg);
		if self.aggr0 == 0:
			self.met0 = self.met0 + met;
		elif self.aggr0 == 1:
			self.met0 = self.met0 + met;
			self.count0 = self.count0 + 1;
		elif self.aggr0 == 2:
			if self.met0 < met:
				self.met0 = met;
		elif self.aggr0 == 3:
			if self.met0 > met:
				self.met0 = met;

	def met_in1(self, msg):
		met = pmt.to_float(msg);
		if self.aggr1 == 0:
			self.met1 = self.met1 + met;
		elif self.aggr1 == 1:
			self.met1 = self.met1 + met;
			self.count1 = self.count1 + 1;
		elif self.aggr1 == 2:
			if self.met1 < met:
				self.met1 = met;
		elif self.aggr1 == 3:
			if self.met1 > met:
				self.met1 = met;

	def met_in2(self, msg):
		met = pmt.to_float(msg);
		if self.aggr2 == 0:
			self.met2 = self.met2 + met;
		elif self.aggr2 == 1:
			self.met2 = self.met2 + met;
			self.count2 = self.count2 + 1;
		elif self.aggr2 == 2:
			if self.met2 < met:
				self.met2 = met;
		elif self.aggr2 == 3:
			if self.met2 > met:
				self.met2 = met;

	def met_in3(self, msg):
		met = pmt.to_float(msg);
		if self.aggr3 == 0:
			self.met3 = self.met3 + met;
		elif self.aggr3 == 1:
			self.met3 = self.met3 + met;
			self.count3 = self.count3 + 1;
		elif self.aggr3 == 2:
			if self.met3 < met:
				self.met3 = met;
		elif self.aggr3 == 3:
			if self.met3 > met:
				self.met3 = met;

	def met_in4(self, msg):
		met = pmt.to_float(msg);
		if self.aggr4 == 0:
			self.met4 = self.met4 + met;
		elif self.aggr4 == 1:
			self.met4 = self.met4 + met;
			self.count4 = self.count4 + 1;
		elif self.aggr4 == 2:
			if self.met4 < met:
				self.met4 = met;
		elif self.aggr4 == 3:
			if self.met4 > met:
				self.met4 = met;

	def met_in5(self, msg):
		met = pmt.to_float(msg);
		if self.aggr5 == 0:
			self.met5 = self.met5 + met;
		elif self.aggr5 == 1:
			self.met5 = self.met5 + met;
			self.count5 = self.count5 + 1;
		elif self.aggr5 == 2:
			if self.met5 < met:
				self.met5 = met;
		elif self.aggr5 == 3:
			if self.met5 > met:
				self.met5 = met;

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

		while True:
			# Handling avg aggregation
			if self.aggr0 == 1 and self.count0 > 0:
				self.met0 = self.met0/self.count0;
			if self.aggr1 == 1 and self.count1 > 0:
				self.met1 = self.met1/self.count1;
			if self.aggr2 == 1 and self.count2 > 0:
				self.met2 = self.met0/self.count2;
			if self.aggr3 == 1 and self.count3 > 0:
				self.met3 = self.met3/self.count3;
			if self.aggr4 == 1 and self.count4 > 0:
				self.met5 = self.met0/self.count5;

			# Write metrics to backlog file
			string = "thr = " + str(self.met0) + ", lat = " + str(self.met1) + ", rnp = " + str(self.met2) + ", interpkt = " + str(self.met3) + ", snr = " + str(self.met4) + ", non = " + str(self.met5);
			f.write(string + "\n");
			print string;

			## START: set portid
			portid = portid + 1;
			if portid > 1:
				portid = 0;
			portid = 1;
			## END: set portid

			if portid == 0:
				print "Active protocol: CSMA/CA"
			elif portid == 1:
				print "Active protocol: TDMA"
				
			## START: select MAC protocol according to portid
			self.message_port_pub(self.msg_port_ctrl_out, pmt.string_to_symbol('portid' + str(portid)));
			## END: select MAC protocol according to portid

			# Reseting metric counters
			self.met0 = self.met1 = self.met2 = self.met3 = self.met4 = self.met5 = 0;
			self.count0 = self.count1 = self.count2 = self.count3 = self.count4 = self.count5 = 0;

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

	# Useful at the beginning, in order to inform normal node to use no MAC protocol (portid = -1)
	def normal_loop(self, name, id):
		global portid;
		portid = -1;

		print "Decision block as Normal node"
		self.message_port_pub(self.msg_port_ctrl_out, pmt.string_to_symbol('portid' + str(portid))); # Sets no MAC protocol at the beginning (portid = -1)

		while True:
			time.sleep(self.metrics_gran);
			msg = "send_metrics";
			self.message_port_pub(self.msg_port_metrics_out, pmt.string_to_symbol(msg));
