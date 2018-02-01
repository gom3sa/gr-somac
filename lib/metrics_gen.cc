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
			message_port_register_out(msg_port_stats_out);

			// Init counters
			pr_appin_count = 0;
			pr_tx_count = 0;
			pr_retx_count = 0;
		}

		void app_in(pmt::pmt_t frame) { // Same frame that is given to "Frame Buffer"
			// TODO
			pr_appin_count++;
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
					pr_tic = clock::now(); // Start counting latency
				}
			}
		}

		void phy_in(pmt::pmt_t frame) {
			pmt::pmt_t cdr = pmt::cdr(frame);
			mac_header *h = (mac_header*)pmt::blob_data(cdr);

			if(h->frame_control == FC_ACK) { // Stats over ACK frames
				if(h->addr1 == pr_curr_frame.addr2 and h->addr2 == pr_curr_frame.addr1 and h->seq_nr == pr_curr_frame.seq_nr) { 
					// ACK bellongs to last sent frame
					pr_toc = clock::now();
					float latency = (float) std::chrono::duration_cast<std::chrono::milliseconds>(pr_toc - pr_tic).count();
					pr_lat_list.push_back(latency);
				}
			}
		}

		void ctrl_in(pmt::pmt_t msg) {
			// TODO: all counters

			// START: calc avg latency
			float sum = 0;
			int count = 0;
			while(pr_lat_list.size() > 0) {
				sum += pr_lat_list[0];
				count++;
				pr_lat_list.pop_front();
			}
			if(count == 0) count = 1; // No division by zero

			float avg_lat = sum/count;
			// END: calc avg latency

			// TODO: build frame and send metrics

			// Reseting counters
			pr_appin_count = 0;
			pr_tx_count = 0;
			pr_retx_count = 0;
		}

	private:
		bool pr_debug;

		// Input msg ports
		pmt::pmt_t msg_port_app_in = pmt::mp("app in");
		pmt::pmt_t msg_port_mac_in = pmt::mp("mac in");
		pmt::pmt_t msg_port_phy_in = pmt::mp("phy in");
		pmt::pmt_t msg_port_ctrl_in = pmt::mp("ctrl in");

		// Output msg ports
		pmt::pmt_t msg_port_stats_out = pmt::mp("stats out");

		// Variables
		mac_header pr_curr_frame;
		uint32_t pr_appin_count, pr_tx_count, pr_retx_count;
		decltype(clock::now()) pr_tic, pr_toc;
		boost::circular_buffer<float> pr_lat_list;

		pmt::pmt_t generate_frame(uint8_t *msdu, int msdu_size, uint16_t fc, uint16_t seq_nr, uint8_t *src_addr, uint8_t *dst_addr) {
			// Inputs: (data, data size, frame control, sequence number, destination address)
			mac_header header;
			header.frame_control = fc;
			header.duration = 0x0000;
			header.seq_nr = seq_nr;

			uint8_t broadcast_addr[6] = {0xff, 0xff, 0xff, 0xff, 0xff, 0xff};

			memcpy(header.addr1, dst_addr, 6);
			memcpy(header.addr2, src_addr, 6);
			memcpy(header.addr3, broadcast_addr, 6);

			uint8_t psdu[1528];
			memcpy(psdu, &header, 24); // Header is 24 bytes long
			memcpy(psdu + 24, msdu, msdu_size); 

			boost::crc_32_type result;
			result.process_bytes(&psdu, 24 + msdu_size);
			uint32_t fcs = result.checksum();

			memcpy(psdu + 24 + msdu_size, &fcs, sizeof(uint32_t));

			// Building frame from cdr & car
			pmt::pmt_t frame = pmt::make_blob(psdu, 24 + msdu_size + sizeof(uint32_t));
			pmt::pmt_t dict = pmt::make_dict();
			dict = pmt::dict_add(dict, pmt::mp("crc_included"), pmt::PMT_T);

			return pmt::cons(dict, frame);
		}
};

metrics_gen::sptr
metrics_gen::make(bool debug) {
	return gnuradio::get_initial_sptr(new metrics_gen_impl(debug));
}