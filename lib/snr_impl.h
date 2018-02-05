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

#ifndef INCLUDED_SOMAC_SNR_IMPL_H
#define INCLUDED_SOMAC_SNR_IMPL_H

#include <somac/snr.h>

namespace gr {
  namespace somac {

    class snr_impl : public snr
    {
     private:
      uint32_t pr_window_size;
      float pr_threshold;
      uint16_t pr_periodicity;
      float pr_noise, pr_signal;
      boost::shared_ptr<gr::thread::thread> pr_thread;

      pmt::pmt_t msg_port_snr_out;

     public:
      snr_impl(uint32_t window_size, float threshold, uint16_t periodicity);
      ~snr_impl();

      void main_loop();
      bool start();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
    };

  } // namespace somac
} // namespace gr

#endif /* INCLUDED_SOMAC_SNR_IMPL_H */

