/* -*- c++ -*- */
/* 
 * Copyright 2018 <+YOU OR YOUR COMPANY+>.
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "metrics_frame.h"
#include <pmt/pmt.h>
#include <string.h>
#include <boost/crc.hpp>

#define FC_PROTOCOL 0x2900
#define CSMA 0x00
#define TDMA 0x01
#define FC_METRICS 0x2100

using namespace gr::somac;

class metrics_frame_impl : public metrics_frame {
	public:
		metrics_frame_impl(std::vector<uint8_t> mac_addr, std::vector<uint8_t> mac_addr_coord)
			: gr::block("metrics_frame",
			gr::io_signature::make(0, 0, 0),
			gr::io_signature::make(0, 0, 0)) {

			message_port_register_in(msg_port_msg_in);
			set_msg_handler(msg_port_msg_in, boost::bind(&metrics_frame_impl::msg_in, this, _1));

			message_port_register_out(msg_port_frame_out);

			for(int i = 0; i < 6; i++) {
				pr_mac_addr[i] = mac_addr[i];
				pr_coord_addr[i] = mac_addr_coord[i];
			}
		}

		void msg_in(pmt::pmt_t msg) {
			std::string str = pmt::symbol_to_string(msg);
			pmt::pmt_t frame;

			if(str == "act_prot:0") {
				uint8_t msdu[1];
				msdu[0] = CSMA;
				frame = generate_frame(msdu, 1, FC_PROTOCOL, 0x0000, pr_coord_addr);
			} else if(str == "act_prot:1") {
				uint8_t msdu[1];
				msdu[0] = TDMA;
				frame = generate_frame(msdu, 1, FC_PROTOCOL, 0x0000, pr_coord_addr);
			} else {
				if(str.length() > 1500) {
					std::cout << "Size of metrics' message exceeds 1500 bytes! Message will not be sent!" << std::endl << std::flush;
					return;
				}

				const char *msdu = str.c_str();
				int msdu_size = str.length();

				frame = generate_frame((uint8_t*)msdu, msdu_size, FC_METRICS, 0x0000, pr_coord_addr);
			}

			message_port_pub(msg_port_frame_out, frame);
		}

	private:
		uint8_t pr_mac_addr[6], pr_coord_addr[6];

		pmt::pmt_t msg_port_msg_in = pmt::mp("msg in");
		pmt::pmt_t msg_port_frame_out = pmt::mp("frame out");

		pmt::pmt_t generate_frame(uint8_t *msdu, int msdu_size, uint16_t fc, uint16_t seq_nr, uint8_t *dst_addr) {
			// Inputs: (data, data size, frame control, sequence number, destination address)
			mac_header header;
			header.frame_control = fc;
			header.duration = 0x0000;
			header.seq_nr = seq_nr;

			memcpy(header.addr1, dst_addr, 6);
			memcpy(header.addr2, pr_mac_addr, 6);
			memcpy(header.addr3, pr_coord_addr, 6);

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

metrics_frame::sptr
metrics_frame::make(std::vector<uint8_t> mac_addr, std::vector<uint8_t> mac_addr_coord) {
	return gnuradio::get_initial_sptr(new metrics_frame_impl(mac_addr, mac_addr_coord));
}