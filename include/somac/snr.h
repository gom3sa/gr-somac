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


#ifndef INCLUDED_SOMAC_SNR_H
#define INCLUDED_SOMAC_SNR_H

#include <somac/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace somac {

    /*!
     * \brief <+description of block+>
     * \ingroup somac
     *
     */
    class SOMAC_API snr : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<snr> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of somac::snr.
       *
       * To avoid accidental use of raw pointers, somac::snr's
       * constructor is in a private implementation
       * class. somac::snr::make is the public interface for
       * creating new instances.
       */
      static sptr make(uint32_t window_size, float threshold, uint16_t periodicity);
    };

  } // namespace somac
} // namespace gr

#endif /* INCLUDED_SOMAC_SNR_H */

