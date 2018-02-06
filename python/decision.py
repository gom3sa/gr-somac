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
	def __init__(self, coord, dec_gran, broad_gran, metrics_gran):
		gr.basic_block.__init__(self, name="decision", in_sig=None, out_sig=None)

		self.coord = coord; # Is coordinator? 
		self.dec_gran = dec_gran; # Granularity of decision
		self.broad_gran = broad_gran;
		self.metrics_gran = metrics_gran;
		# TODO: if node has not got portid from network, it should wait and transmit nothing. Perhaps change portid to an invalid one;

		# Input ports
		self.msg_port_act_prot_in = pmt.intern('act prot in');
		self.message_port_register_in(self.msg_port_act_prot_in);
		self.set_msg_handler(self.msg_port_act_prot_in, self.act_prot_in);

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

		print "Decision block as Coordinator"

		while True:
			## START: set portid
			portid = portid + 1;
			if portid > 1:
				portid = 0;
			## END: set portid

			if portid == 0:
				print "Active protocol: CSMA/CA"
			elif portid == 1:
				print "Active protocol: TDMA"
				
			## START: select MAC protocol according to portid
			self.message_port_pub(self.msg_port_ctrl_out, pmt.string_to_symbol('portid' + str(portid)));
			time.sleep(self.dec_gran);
			## END: select MAC protocol according to portid

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