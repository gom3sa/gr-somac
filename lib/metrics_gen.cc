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
#define BUFFER_SIZE 1024
#define MAX_SEQ_NR 65536

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
			message_port_register_in(msg_port_new_frame_in);
			set_msg_handler(msg_port_new_frame_in, boost::bind(&metrics_gen_impl::new_frame_in, this, _1));

			message_port_register_in(msg_port_mac_in);
			set_msg_handler(msg_port_mac_in, boost::bind(&metrics_gen_impl::mac_in, this, _1));

			message_port_register_in(msg_port_phy_in);
			set_msg_handler(msg_port_phy_in, boost::bind(&metrics_gen_impl::phy_in, this, _1));

			message_port_register_in(msg_port_buffer_in);
			set_msg_handler(msg_port_buffer_in, boost::bind(&metrics_gen_impl::buffer_in, this, _1));

			message_port_register_in(msg_port_snr_in);
			set_msg_handler(msg_port_snr_in, boost::bind(&metrics_gen_impl::snr_in, this, _1));

			message_port_register_in(msg_port_ctrl_in);
			set_msg_handler(msg_port_ctrl_in, boost::bind(&metrics_gen_impl::ctrl_in, this, _1));

			// Output msg ports
			message_port_register_out(msg_port_broad_out);

			// Init counters
			pr_nfin_count 				= 0;
			pr_tx_count 				= 0;
			pr_retx_count 				= 0;
			pr_ack_count 				= 0;
			pr_last_seq_nr_from_buff 	= 0;
			pr_interpkt_tic 			= clock::now();
			pr_thr_tic 					= clock::now();

			pr_interpkt_list.rset_capacity(BUFFER_SIZE);
			pr_lat_list.rset_capacity(BUFFER_SIZE);
			pr_snr_list.rset_capacity(BUFFER_SIZE);
			pr_contention_list.rset_capacity(BUFFER_SIZE);
		}

		void new_frame_in(pmt::pmt_t frame) { // Brand new frame, same that goes to Frame Buffer
			// Buffer size
			pmt::pmt_t cdr = pmt::cdr(frame);
			mac_header *h = (mac_header*)pmt::blob_data(cdr);
			pr_last_seq_nr_from_buff = h->seq_nr;

			// Interpacket delay
			pr_nfin_count++;

			pr_interpkt_toc = clock::now();
			float interpkt_delay = (float) std::chrono::duration_cast<std::chrono::milliseconds>(pr_interpkt_toc - pr_interpkt_tic).count();
			
			// So it ignores long periods (5s) with no traffic being generated
			if(interpkt_delay < 5000) {
				pr_interpkt_list.push_back(interpkt_delay);
			}

			pr_interpkt_tic = clock::now();
		}

		void mac_in(pmt::pmt_t frame) { // Same frame that is given to PHY
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

					// Contention
					auto toc = clock::now();
					float dt = (float) std::chrono::duration_cast<std::chrono::milliseconds>(toc - pr_contention_tic[(int)h->seq_nr]).count();
					pr_contention_list.push_back(dt);
				}
			}
		}

		void phy_in(pmt::pmt_t frame) {
			pmt::pmt_t cdr = pmt::cdr(frame);
			mac_header *h = (mac_header*)pmt::blob_data(cdr);

			if(h->frame_control == FC_ACK) { // Stats over ACK frames
				if(memcmp(h->addr1, pr_curr_frame.addr2, 6) == 0 and memcmp(h->addr2, pr_curr_frame.addr1, 6) == 0
						and h->seq_nr == pr_curr_frame.seq_nr) {
					// ACK bellongs to last sent frame
					pr_ack_count++;
					pr_lat_toc = clock::now();
					float latency = (float) std::chrono::duration_cast<std::chrono::milliseconds>(pr_lat_toc - pr_lat_tic[(int)h->seq_nr]).count();
					pr_lat_list.push_back(latency);
				}
			}
		}

		void buffer_in(pmt::pmt_t frame) {
			// Frame from buffer
			pmt::pmt_t cdr = pmt::cdr(frame);
			mac_header *h = (mac_header*)pmt::blob_data(cdr);
			pr_lat_tic[(int)h->seq_nr] = clock::now();
			pr_contention_tic[(int)h->seq_nr] = clock::now();
		}

		void snr_in(pmt::pmt_t msg) {
			pr_snr_list.push_back(pmt::to_float(msg));
		}

		void ctrl_in(pmt::pmt_t msg) {
			// TODO: all counters
			if(pmt::symbol_to_string(msg) == "send_metrics") {
				if(pr_debug) std::cout << "Metrics were requested. Calculation starts now." << std::endl << std::flush;
				// Common variables
				double sum;
				int count, c;
				float elapsed_time;

				// START: calc avg jitter
				sum = 0; 
				count = 0;
				c = pr_lat_list.size();
				while(c-- >= 2) {
					sum += std::abs(pr_lat_list[c-1] - pr_lat_list[c-2]);
					count++;
				}
				if(count == 0) {
					count = 1;
				}
				float avg_jitter = sum/count;
				if(pr_debug) std::cout << "Jitter = " << avg_jitter << std::endl << std::flush;
				// END: calc avg jitter

				// START: calc avg latency (ms)
				sum = 0;
				count = 0;
				c = pr_lat_list.size();
				while(c-- > 0) {
					sum += pr_lat_list[0];
					count++;
					pr_lat_list.pop_front();
				}
				if(count == 0) {
					count = 1; // No division by zero
				}
				float avg_lat = sum/count;
				if(pr_debug) std::cout << "Latency (ms) = " << avg_lat << std::endl << std::flush;
				// END: calc avg latency

				// START: calc avg interpacket dealy (ms)
				sum = 0;
				count = 0;
				c = pr_interpkt_list.size();
				while(c-- > 0) {
					sum += pr_interpkt_list[0];
					count++;
					pr_interpkt_list.pop_front();
				}
				if(count == 0) {
					count = 1;
				}
				float avg_interpkt = sum/count;
				if(pr_debug) std::cout << "Interpacket delay (ms) = " << avg_interpkt << std::endl << std::flush;
				// END: calc avg interpacket dealy (ms)

				// START: calc RNP (required number of packet transmissions)
				float rnp = 0;
				if(pr_tx_count + pr_retx_count > 0 and pr_ack_count > 0) {
					rnp = ((pr_tx_count + pr_retx_count)/pr_ack_count) - 1;
				}
				std::cout << "pr_tx_count = " << pr_tx_count << ", pr_retx_count = " << pr_retx_count << ", pr_ack_count = " << pr_ack_count << std::endl << std::flush;
				if(pr_debug) std::cout << "RNP = " << rnp << std::endl << std::flush;
				// END: calc RNP (required number of packet transmissions)

				// START: calc throughput (frame/s)
				pr_thr_toc = clock::now();
				elapsed_time = (float) std::chrono::duration_cast<std::chrono::seconds>(pr_thr_toc - pr_thr_tic).count();
				float thr = pr_ack_count/elapsed_time;
				if(pr_debug) std::cout << "Throughput (frame/s) = " << thr << std::endl << std::flush;
				// END: calc throughput (frame/s)

				// START: calc avg SNR
				sum = 0;
				count = 0;
				c = pr_snr_list.size();
				while(c-- > 0) {
					sum += pr_snr_list[0];
					count++;
					pr_snr_list.pop_front();
				}
				if(count == 0) count = 1; // No division by zero
				float avg_snr = sum/count;
				if(pr_debug) std::cout << "SNR (dB) = " << avg_snr << std::endl << std::flush;
				// END: calc avg SNR

				// START: calc avg contention
				sum = 0;
				count = 0;
				c = pr_contention_list.size();
				while(c-- > 0) {
					sum += pr_contention_list[0];
					count++;
					pr_contention_list.pop_front();
				}
				if(count == 0) count = 1;
				float avg_cont = sum/count;
				if(pr_debug) std::cout << "Contention (ms) = " << avg_cont << std::endl << std::flush;
				// END: calc avg contention

				// START: estimates buffer size
				float buff_size;
				uint16_t curr_seq_nr = pr_curr_frame.seq_nr;

				if(pr_last_seq_nr_from_buff >= curr_seq_nr) {
					buff_size = pr_last_seq_nr_from_buff - curr_seq_nr;
				} else {
					buff_size = pr_last_seq_nr_from_buff + MAX_SEQ_NR - curr_seq_nr;
				}
				// END: estimates buffer size

				// max(msdu) = max(psdu) - (24 (header) + 4 (fcs)) = 1500 bytes
				std::string str = "lat=" + std::to_string(avg_lat) + ":jitter=" + std::to_string(avg_jitter) +
					":interpkt=" + std::to_string(avg_interpkt) + ":rnp=" + std::to_string(rnp) +
					":thr=" + std::to_string(thr) + ":snr=" + std::to_string(avg_snr) +
					":cont=" + std::to_string(avg_cont) + ":buffsize=" + std::to_string(buff_size);

				pmt::pmt_t metrics = pmt::string_to_symbol(str);

				message_port_pub(msg_port_broad_out, metrics);

				// Reseting counters
				pr_nfin_count = 0;
				pr_tx_count = 0;
				pr_retx_count = 0;
				pr_ack_count = 0;
				pr_thr_tic = clock::now();
			}
		}

	private:
		bool pr_debug;

		// Input msg ports
		pmt::pmt_t msg_port_new_frame_in = pmt::mp("new frame in");
		pmt::pmt_t msg_port_mac_in = pmt::mp("mac in");
		pmt::pmt_t msg_port_phy_in = pmt::mp("phy in");
		pmt::pmt_t msg_port_buffer_in = pmt::mp("buffer in");
		pmt::pmt_t msg_port_snr_in = pmt::mp("snr in");
		pmt::pmt_t msg_port_ctrl_in = pmt::mp("ctrl in");

		// Output msg ports
		pmt::pmt_t msg_port_broad_out = pmt::mp("broad out");

		// Variables
		mac_header pr_curr_frame;
		decltype(clock::now()) pr_lat_tic[MAX_SEQ_NR], pr_contention_tic[MAX_SEQ_NR];
		int pr_nfin_count, pr_tx_count, pr_retx_count, pr_ack_count;
		decltype(clock::now()) pr_lat_toc, pr_interpkt_tic, pr_interpkt_toc, pr_thr_tic, pr_thr_toc;
		boost::circular_buffer<float> pr_lat_list, pr_interpkt_list, pr_snr_list, pr_contention_list;
		uint16_t pr_last_seq_nr_from_buff;
};

metrics_gen::sptr
metrics_gen::make(bool debug) {
	return gnuradio::get_initial_sptr(new metrics_gen_impl(debug));
}
