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
#include "metrics_gen.h"
#include <pmt/pmt.h>
#include <chrono>
#include <boost/circular_buffer.hpp>
#include <boost/crc.hpp>

#define FC_ACK 0x2B00
#define FC_DATA 0x0008
#define FC_METRICS 0x2100

using namespace gr::somac;

class metrics_gen_impl : public metrics_gen {
	typedef std::chrono::high_resolution_clock clock;

	public:
		metrics_gen_impl(bool debug)
			: gr::block("metrics_gen",
				gr::io_signature::make(0, 0, 0),
				gr::io_signature::make(0, 0, 0)),
				pr_debug(debug) {

			// Input msg ports
			message_port_register_in(msg_port_app_in);
			set_msg_handler(msg_port_app_in, boost::bind(&metrics_gen_impl::app_in, this, _1));

			message_port_register_in(msg_port_mac_in);
			set_msg_handler(msg_port_mac_in, boost::bind(&metrics_gen_impl::mac_in, this, _1));

			message_port_register_in(msg_port_phy_in);
			set_msg_handler(msg_port_phy_in, boost::bind(&metrics_gen_impl::phy_in, this, _1));

			message_port_register_in(msg_port_ctrl_in);
			set_msg_handler(msg_port_ctrl_in, boost::bind(&metrics_gen_impl::ctrl_in, this, _1));

			// Output msg ports
			message_port_register_out(msg_port_broad_out);

			// Init counters
			pr_appin_count = 0;
			pr_tx_count = 0;
			pr_retx_count = 0;
			pr_ack_count = 0;
			pr_interpkt_tic = clock::now();
			pr_thr_tic = clock::now();
		}

		void app_in(pmt::pmt_t frame) { // Same frame that is given to "Frame Buffer"
			// TODO
			pr_appin_count++;

			pr_interpkt_toc = clock::now();
			float interpkt_delay = (float) std::chrono::duration_cast<std::chrono::milliseconds>(pr_interpkt_toc - pr_interpkt_tic).count();
			pr_interpkt_list.push_back(interpkt_delay);
			pr_interpkt_tic = clock::now();
		}

		void mac_in(pmt::pmt_t frame) { // Same frame that is given to PHY
			// TODO
			pmt::pmt_t cdr = pmt::cdr(frame);
			mac_header *h = (mac_header*)pmt::blob_data(cdr);

			if(h->frame_control == FC_DATA) { // Stats only over data frames
				if(memcmp(h, &pr_curr_frame, 24) == 0) { // Same header, retransmission
					pr_retx_count++;
				} else { // A new transmission
					pr_curr_frame.frame_control = h->frame_control;
					pr_curr_frame.duration = h->duration;
					memcpy(&pr_curr_frame.addr1, h->addr1, 18); // Copying addr1, addr2 and addr3 at once
					pr_curr_frame.seq_nr = h->seq_nr;

					pr_tx_count++;
					pr_lat_tic = clock::now(); // Start counting latency
				}
			}
		}

		void phy_in(pmt::pmt_t frame) {
			pmt::pmt_t cdr = pmt::cdr(frame);
			mac_header *h = (mac_header*)pmt::blob_data(cdr);

			if(h->frame_control == FC_ACK) { // Stats over ACK frames
				if(h->addr1 == pr_curr_frame.addr2 and h->addr2 == pr_curr_frame.addr1 and h->seq_nr == pr_curr_frame.seq_nr) { 
					// ACK bellongs to last sent frame
					pr_ack_count++;
					pr_lat_toc = clock::now();
					float latency = (float) std::chrono::duration_cast<std::chrono::milliseconds>(pr_lat_toc - pr_lat_tic).count();
					pr_lat_list.push_back(latency);
				}
			}
		}

		void ctrl_in(pmt::pmt_t msg) {
			// TODO: all counters
			if(pmt::symbol_to_string(msg) == "send_metrics") {
				if(pr_debug) std::cout << "Metrics were requested. Calculation starts now." << std::endl << std::flush;
				// Common variables
				float sum;
				int count;
				float elapsed_time;

				// START: calc avg latency (ms)
				if(pr_debug) std::cout << "Calculating: latency" << std::endl << std::flush;
				sum = 0;
				count = 0;
				while(pr_lat_list.size() > 0) {
					sum += pr_lat_list[0];
					count++;
					pr_lat_list.pop_front();
				}
				if(count == 0) count = 1; // No division by zero
				float avg_lat = sum/count;
				// END: calc avg latency

				// START: calc avg interpacket dealy (ms)
				if(pr_debug) std::cout << "Calculating: interpacket delay" << std::endl << std::flush;
				sum = 0;
				count = 0;
				while(pr_interpkt_list.size() > 0) {
					sum += pr_interpkt_list[0];
					count++;
					pr_interpkt_list.pop_front();
				}
				if(count == 0) count = 1;
				float avg_interpkt = sum/count;
				// END: calc avg interpacket dealy (ms)

				// START: calc RNP (required number of packet transmissions)
				if(pr_debug) std::cout << "Calculating: rnp" << std::endl << std::flush;
				float rnp = (pr_tx_count + pr_retx_count)/(pr_ack_count + 1) - 1;
				// END: calc RNP (required number of packet transmissions)

				// START: calc throughput (frame/s)
				if(pr_debug) std::cout << "Calculating: throughput" << std::endl << std::flush;
				pr_thr_toc = clock::now();
				elapsed_time = (float) std::chrono::duration_cast<std::chrono::seconds>(pr_thr_toc - pr_thr_tic).count();
				float thr = pr_ack_count/elapsed_time;
				// END: calc throughput (frame/s)

				// max(msdu) = max(psdu) - (24 (header) + 4 (fcs)) = 1500 bytes
				std::string str = "lat=" + std::to_string(avg_lat) + ":interpkt=" + std::to_string(avg_interpkt) + ":rnp=" + std::to_string(rnp) + ":thr=" + std::to_string(thr); 
				pmt::pmt_t metrics = pmt::string_to_symbol(str);

				message_port_pub(msg_port_broad_out, metrics);

				// Reseting counters
				pr_appin_count = 0;
				pr_tx_count = 0;
				pr_retx_count = 0;
				pr_ack_count = 0;
				pr_thr_tic = clock::now();
			}
		}

	private:
		bool pr_debug;

		// Input msg ports
		pmt::pmt_t msg_port_app_in = pmt::mp("app in");
		pmt::pmt_t msg_port_mac_in = pmt::mp("mac in");
		pmt::pmt_t msg_port_phy_in = pmt::mp("phy in");
		pmt::pmt_t msg_port_ctrl_in = pmt::mp("ctrl in");

		// Output msg ports
		pmt::pmt_t msg_port_broad_out = pmt::mp("broad out");

		// Variables
		mac_header pr_curr_frame;
		uint32_t pr_appin_count, pr_tx_count, pr_retx_count, pr_ack_count;
		decltype(clock::now()) pr_lat_tic, pr_lat_toc, pr_interpkt_tic, pr_interpkt_toc, pr_thr_tic, pr_thr_toc;
		boost::circular_buffer<float> pr_lat_list, pr_interpkt_list;
};

metrics_gen::sptr
metrics_gen::make(bool debug) {
	return gnuradio::get_initial_sptr(new metrics_gen_impl(debug));
}