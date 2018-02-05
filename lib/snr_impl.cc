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
#include "snr_impl.h"
#include <pmt/pmt.h>
#include <unistd.h>
#include <string.h>
#include <cstdlib>

#define MAX_INPUT_SIGNAL -30
#define LOWER_THRESHOLD -150
#define ALPHA 0.001

namespace gr {
	namespace somac {
		snr::sptr
		snr::make(uint32_t window_size, float threshold, uint16_t periodicity) {
			return gnuradio::get_initial_sptr
				(new snr_impl(window_size, threshold, periodicity));
		}
		/*
		 * The private constructor
		 */
		snr_impl::snr_impl(uint32_t window_size, float threshold, uint16_t periodicity)
			: gr::block("snr",
							gr::io_signature::make(1, 1, sizeof(float)),
							gr::io_signature::make(0, 0, 0)) {

			pr_window_size = window_size;
			pr_threshold = threshold;
			pr_periodicity = periodicity;
			pr_noise = 0;
			pr_signal = 0;

			msg_port_snr_out = pmt::mp("snr out");
			message_port_register_out(msg_port_snr_out);
		}

		snr_impl::~snr_impl() {}

		bool snr_impl::start() {
			pr_thread = boost::shared_ptr<gr::thread::thread> (new gr::thread::thread(boost::bind(&snr_impl::main_loop, this)));
		}

		void snr_impl::main_loop() {
			float snr;

			while(true) {
				usleep(pr_periodicity*1000000);

				snr = pr_signal - pr_noise;
				if(snr < 0) snr = 0;

				message_port_pub(msg_port_snr_out, pmt::from_float(snr));
			}
		}

		void snr_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required) {
			ninput_items_required[0] = pr_window_size*noutput_items;
		}

		int snr_impl::general_work (int noutput_items,
											 gr_vector_int &ninput_items,
											 gr_vector_const_void_star &input_items,
											 gr_vector_void_star &output_items) {
			const float *in = (const float *) input_items[0];

			float noise_sum = 0;
			float noise_count = 0;
			float signal_sum = 0;
			float signal_count = 0;
			float power; 

			for(int i = 0; i < noutput_items; i++) {
				power = in[i];

				if(power > LOWER_THRESHOLD and power < pr_threshold) {
					noise_sum += power;
					noise_count++;
				} else if (power >= pr_threshold and power < MAX_INPUT_SIGNAL) {
					signal_sum += power;
					signal_count++;
				}
			}

			if(noise_count != 0) {
				pr_noise = (noise_sum/ noise_count)*ALPHA + (1 - ALPHA)*pr_noise;
			}
			
			if(signal_count != 0) {
				pr_signal = (signal_sum/ signal_count)*ALPHA + (1 - ALPHA)*pr_signal;
			}

			consume_each (noutput_items);
			return noutput_items;
		}
	} /* namespace fsmac */
} /* namespace gr */

