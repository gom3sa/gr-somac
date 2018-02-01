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
#include "broadcaster.h"
#include <pmt/pmt.h>
#include <string.h>
#include <boost/crc.hpp>

#define FC_PROTOCOL 0x2900
#define CSMA 0x00
#define TDMA 0x01

using namespace gr::somac;

class broadcaster_impl : public broadcaster {
	public:
		broadcaster_impl(std::vector<uint8_t> mac_addr)
			: gr::block("broadcaster",
			gr::io_signature::make(0, 0, 0),
			gr::io_signature::make(0, 0, 0)) {

			message_port_register_in(msg_port_msg_in);
			set_msg_handler(msg_port_msg_in, boost::bind(&broadcaster_impl::msg_in, this, _1));

			message_port_register_out(msg_port_frame_out);

			for(int i = 0; i < 6; i++) {
				pr_mac_addr[i] = mac_addr[i];
				pr_broadcast_addr[i] = 0xff;
			}
		}

	void msg_in(pmt::pmt_t msg) {
		std::string str = pmt::symbol_to_string(msg);
		uint8_t act_prot;

		if(str == "act_prot:0") act_prot = CSMA;
		else if(str == "act_prot:1") act_prot = TDMA;
		else return;

		uint8_t msdu[1];
		msdu[0] = act_prot;
		int msdu_size = 1;

		pmt::pmt_t frame = generate_frame(msdu, msdu_size, FC_PROTOCOL, 0x0000, pr_broadcast_addr);
		message_port_pub(msg_port_frame_out, frame);
	}

	pmt::pmt_t generate_frame(uint8_t *msdu, int msdu_size, uint16_t fc, uint16_t seq_nr, uint8_t *dst_addr) {
		// Inputs: (data, data size, frame control, sequence number, destination address)
		mac_header header;
		header.frame_control = fc;
		header.duration = 0x0000;
		header.seq_nr = seq_nr;

		memcpy(header.addr1, dst_addr, 6);
		memcpy(header.addr2, pr_mac_addr, 6);
		memcpy(header.addr3, pr_broadcast_addr, 6);

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

	private:
		uint8_t pr_mac_addr[6], pr_broadcast_addr[6];

		pmt::pmt_t msg_port_msg_in = pmt::mp("msg in");
		pmt::pmt_t msg_port_frame_out = pmt::mp("frame out");
};

broadcaster::sptr
broadcaster::make(std::vector<uint8_t> mac_addr) {
	return gnuradio::get_initial_sptr(new broadcaster_impl(mac_addr));
}