/* -*- c++ -*- */
/* 
 * Copyright 2018 André Gomes, UFMG - <andre.gomes@dcc.ufmg.br>.
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.	If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "sensor.h"
#include <pmt/pmt.h>

#define FC_ACK 0x2B00
#define FC_DATA 0x0008
// FC reserved to TDMA
#define FC_SYNC 0x2000 // Frame Control for SYNC
#define FC_ALLOC 0x2800 // Frame Control for Allocation
#define FC_REQ 0x2400 // Frame Control for Requesting a slot during allocation
#define FC_SKIP 0x2C00 // Frame Control for Skipping a slot during allocation (slot not allocated)
// Informs the protocol in use on the network
#define FC_PROTOCOL 0x2900 // Active protocol on network
#define CSMA 0x00
#define TDMA 0x01

using namespace gr::somac;

class sensor_impl : public sensor {
	public:
		sensor_impl(std::vector<uint8_t> mac, bool debug)
			: gr::block("sensor", gr::io_signature::make(0, 0, 0), gr::io_signature::make(0, 0, 0)),
			pr_debug(debug) {

			// Input ports
			message_port_register_in(msg_port_phy_in);
			set_msg_handler(msg_port_phy_in, boost::bind(&sensor_impl::phy_in, this, _1));

			// Output ports
			message_port_register_out(msg_port_act_prot_out);

			for(int i = 0; i < 6; i++) {
				pr_mac[i] = mac[i];
				pr_broadcast[i] = 0xff;
			}
		}

		void phy_in(pmt::pmt_t frame) {
			pmt::pmt_t cdr = pmt::cdr(frame);
			mac_header *h = (mac_header*)pmt::blob_data(cdr); // Frame's header

			int is_broadcast = memcmp(h->addr1, pr_broadcast, 6); // 0 if frame IS for broadcast
			int is_mine = memcmp(h->addr1, pr_mac, 6); // 0 if frame IS mine

			if(is_mine != 0 and is_broadcast != 0) {
				if(pr_debug) std::cout << "Neither for me nor broadcast" << std::endl << std::flush;
				return;
			}

			uint8_t *f = (uint8_t*)pmt::blob_data(cdr); // Get the complete frame rather than just the header
			int f_len = pmt::blob_length(cdr) - 24; // Strips header

			switch(h->frame_control) {
				case FC_PROTOCOL: {
					if(is_broadcast == 0) {
						uint8_t prot[1];
						memcpy(prot, f + 24, 1);

						switch(prot[0]) {
							case CSMA: {
								pr_protocol = 0;
								if(pr_debug) std::cout << "Active protocol: CSMA/CA" << std::endl << std::flush;
							} break; 

							case TDMA: {
								pr_protocol = 1;
								if(pr_debug) std::cout << "Active protocol: TDMA" << std::endl << std::flush;
							} break; 

							default: {
								if(pr_debug) std::cout << "Active protocol: Unknwon" << std::endl << std::flush;
								return;
							}
						}

						pmt::pmt_t msg = pmt::from_long(pr_protocol);
						message_port_pub(msg_port_act_prot_out, msg);
					}
				}
			}
		}

	private:
		bool pr_debug;
		uint8_t pr_mac[6], pr_broadcast[6];
		int pr_protocol;

		// Input ports
		pmt::pmt_t msg_port_phy_in = pmt::mp("phy in");

		// Output ports
		pmt::pmt_t msg_port_act_prot_out = pmt::mp("act prot out");
};

sensor::sptr
sensor::make(std::vector<uint8_t> mac, bool debug) {
	return gnuradio::get_initial_sptr (new sensor_impl(mac, debug));
}