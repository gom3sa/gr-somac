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
#include <boost/thread.hpp>
#include <time.h>
#include <chrono>

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
#define FC_METRICS 0x2100
// In order to set the buffer size of some counters
#define MAX_NON 256
// Time to reset counters
#define GRANULARITY 30

using namespace gr::somac;

struct metrics {
	float thr;
	float lat;
	float rnp;
	float interpkt;
	float snr;
	float contention;

	decltype(std::chrono::high_resolution_clock::now()) tstamp;
};

class sensor_impl : public sensor {
	typedef std::chrono::high_resolution_clock clock;

	public:
		sensor_impl(std::vector<uint8_t> mac, bool is_coord, bool debug)
			: gr::block("sensor", gr::io_signature::make(0, 0, 0), gr::io_signature::make(0, 0, 0)),
			pr_is_coord(is_coord), pr_debug(debug) {

			// Input ports
			message_port_register_in(msg_port_phy_in);
			set_msg_handler(msg_port_phy_in, boost::bind(&sensor_impl::phy_in, this, _1));

			// Output ports
			message_port_register_out(msg_port_act_prot_out);
			message_port_register_out(msg_port_met_out0);
			message_port_register_out(msg_port_met_out1);
			message_port_register_out(msg_port_met_out2);
			message_port_register_out(msg_port_met_out3);
			message_port_register_out(msg_port_met_out4);
			message_port_register_out(msg_port_met_out5);
			message_port_register_out(msg_port_met_out6);

			for(int i = 0; i < 6; i++) {
				pr_mac[i] = mac[i];
				pr_broadcast[i] = 0xff;
			}

			for(int id = 0; id < 256; id++) { // id is related to the last byte of mac addr
				pr_metrics[id].thr = 0;
				pr_metrics[id].lat = 0;
				pr_metrics[id].rnp = 0;
				pr_metrics[id].interpkt = 0;
				pr_metrics[id].snr = 0;
				pr_metrics[id].contention = 0;
				pr_metrics[id].tstamp = clock::now();
			}

			pr_non = 0;
		}

		bool start() {
			if(pr_is_coord) thread_reset_counters = boost::shared_ptr<gr::thread::thread> (new gr::thread::thread(boost::bind(&sensor_impl::reset, this)));
			return block::start();
		}

		void reset() { // Reset counters and send metrics to decision block
			int count = 0;

			while(true) {
				sleep(GRANULARITY);

				int id;
				int non = 0;
				auto tnow = clock::now();
				float dt;
				for(int i = 0; i < pr_non; i++) {
					id = (int) pr_addr_list[i*6 + 5];

					dt = (float) std::chrono::duration_cast<std::chrono::seconds>(tnow - pr_metrics[id].tstamp).count();
					if(dt < 2*GRANULARITY) {
						if(pr_debug) std::cout << "lat sensor [" << id << "] = " << pr_metrics[id].lat << std::endl << std::flush;
						message_port_pub(msg_port_met_out0, pmt::from_float(pr_metrics[id].thr));
						message_port_pub(msg_port_met_out1, pmt::from_float(pr_metrics[id].lat));
						message_port_pub(msg_port_met_out2, pmt::from_float(pr_metrics[id].rnp));
						message_port_pub(msg_port_met_out3, pmt::from_float(pr_metrics[id].interpkt));
						message_port_pub(msg_port_met_out4, pmt::from_float(pr_metrics[id].snr));
						message_port_pub(msg_port_met_out5, pmt::from_float(pr_metrics[id].contention));
						non++;
					} else {
						if(pr_debug) std::cout << "Node " << id << " had a timeout" << std::endl << std::flush;
					}
				}
				message_port_pub(msg_port_met_out6, pmt::from_float(non));
			}
		}

		void phy_in(pmt::pmt_t frame) {
			pmt::pmt_t cdr = pmt::cdr(frame);
			mac_header *h = (mac_header*)pmt::blob_data(cdr); // Frame's header

			int is_broadcast = memcmp(h->addr1, pr_broadcast, 6); // 0 if frame IS for broadcast
			int is_mine = memcmp(h->addr1, pr_mac, 6); // 0 if frame IS mine
			int from_me = memcmp(h->addr2, pr_mac, 6); // 0 if I generated the frame

			if(is_mine != 0 and is_broadcast != 0) {
				if(pr_debug) std::cout << "Neither for me nor broadcast" << std::endl << std::flush;
				return;
			}

			uint8_t *f = (uint8_t*)pmt::blob_data(cdr); // Get the complete frame rather than just the header
			int f_len = pmt::blob_length(cdr) - 24; // Strips header

			// Counting active nodes
			if(pr_is_coord and from_me != 0) { // Does not count itself as a node in the network
				bool listed = false;
				for(int i = 0; i < pr_non; i++) {
					if(memcmp(h->addr2, pr_addr_list + i*6, 6) == 0) {
						listed = true;
					}
				}
				if(!listed) { // Addr is not listed, so add it to the addr list
					memcpy(pr_addr_list + pr_non*6, h->addr2, 6);
					pr_non++;
				}
				int id = (int) h->addr2[5];
				pr_metrics[id].tstamp = clock::now();
			}

			switch(h->frame_control) {
				case FC_PROTOCOL: {
					if(is_broadcast == 0 and from_me != 0 and !pr_is_coord) {
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
				} break;

				case FC_METRICS: {
					if(is_broadcast == 0 and from_me != 0 and pr_is_coord) {
						char msdu[f_len + 1];
						msdu[f_len] = '\0'; // End of string
						memcpy(msdu, f + 24, f_len);

						std::string str(msdu);

						int id = (int) h->addr2[5];
						parse_metrics(str, id);
						pr_count++;
					}
				} break;

				default: {
					return;
				}
			}
		}

	private:
		bool pr_is_coord, pr_debug;
		uint8_t pr_mac[6], pr_broadcast[6], pr_addr_list[6*MAX_NON];
		int pr_protocol, pr_non, pr_count;
		metrics pr_metrics[256];

		// Threads
		boost::shared_ptr<gr::thread::thread> thread_reset_counters;

		// Input ports
		pmt::pmt_t msg_port_phy_in = pmt::mp("phy in");

		// Output ports
		pmt::pmt_t msg_port_act_prot_out = pmt::mp("act prot out");
		pmt::pmt_t msg_port_met_out0 = pmt::mp("met thr");
		pmt::pmt_t msg_port_met_out1 = pmt::mp("met lat");
		pmt::pmt_t msg_port_met_out2 = pmt::mp("met rnp");
		pmt::pmt_t msg_port_met_out3 = pmt::mp("met interpkt");
		pmt::pmt_t msg_port_met_out4 = pmt::mp("met snr");
		pmt::pmt_t msg_port_met_out5 = pmt::mp("met contention");
		pmt::pmt_t msg_port_met_out6 = pmt::mp("met non");

		void parse_metrics(std::string str, int id) {
			size_t len, s, e;
			float lat, thr, rnp;
			int eos = 1;

			while(str.length() > 0) {
				len = str.length();
				s = str.find("=") + 1;
				e = str.find(":");

				if(e == -1) { // last metris
					e = len;
					eos--;
				}

				// Summing up metrics
				std::string aux = str.substr(0, s);
				if(aux == "lat=") {
					pr_metrics[id].lat = std::stof(str.substr(s, e - s));
					if(pr_debug) std::cout << "lat=" << std::stof(str.substr(s, e - s)) << std::endl;
				} else if(aux == "interpkt=") {
					pr_metrics[id].interpkt = std::stof(str.substr(s, e - s));
					if(pr_debug) std::cout << "interpkt=" << std::stof(str.substr(s, e - s)) << std::endl;
				} else if(aux == "rnp=") {
					pr_metrics[id].rnp = std::stof(str.substr(s, e - s));
					if(pr_debug) std::cout << "rnp=" << std::stof(str.substr(s, e - s)) << std::endl;
				} else if(aux == "thr=") {
					pr_metrics[id].thr = std::stof(str.substr(s, e - s));
					if(pr_debug) std::cout << "thr=" << std::stof(str.substr(s, e - s)) << std::endl;
				} else if(aux == "snr=") {
					pr_metrics[id].snr = std::stof(str.substr(s, e - s));
					if(pr_debug) std::cout << "snr=" << std::stof(str.substr(s, e - s)) << std::endl;
				} else if(aux == "cont") {
					pr_metrics[id].contention = std::stof(str.substr(s, e - s));
					if(pr_debug) std::cout << "cont=" << std::stof(str.substr(s, e - s)) << std::endl;
				}

				str = str.substr(e + eos, len - e);
			}
		}
};

sensor::sptr
sensor::make(std::vector<uint8_t> mac, bool is_coord, bool debug) {
	return gnuradio::get_initial_sptr (new sensor_impl(mac, is_coord, debug));
}
