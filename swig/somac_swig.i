/* -*- c++ -*- */

#define SOMAC_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "somac_swig_doc.i"

%{
#include "somac/sensor.h"
#include "somac/broadcaster.h"
#include "somac/metrics_gen.h"
%}


%include "somac/sensor.h"
GR_SWIG_BLOCK_MAGIC2(somac, sensor);
%include "somac/broadcaster.h"
GR_SWIG_BLOCK_MAGIC2(somac, broadcaster);
%include "somac/metrics_gen.h"
GR_SWIG_BLOCK_MAGIC2(somac, metrics_gen);
