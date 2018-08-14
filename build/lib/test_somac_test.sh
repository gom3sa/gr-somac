#!/bin/sh
export VOLK_GENERIC=1
export GR_DONT_LOAD_PREFS=1
export srcdir=/home/sdr/gr-somac/lib
export GR_CONF_CONTROLPORT_ON=False
export PATH=/home/sdr/gr-somac/build/lib:$PATH
export LD_LIBRARY_PATH=/home/sdr/gr-somac/build/lib:$LD_LIBRARY_PATH
export PYTHONPATH=$PYTHONPATH
test-somac 
