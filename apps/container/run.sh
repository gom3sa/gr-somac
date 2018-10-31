#!/bin/bash

ARG_ID=$1
MODE=$2

# IDs of TunTap script
IDS_CONFIG=(1 2 3 4 5 6 7 8 9 GATEWAY)
# IDs of the 1st round 
IDS_1=(1 6 8 2 7 9 3 4 5)
# IDs of the 2nd round
IDS_2=(5 1 4 6 2 3 7 8 9)

# Setup {{{
PROT=$MODE; # 0: CSMA, 1: TDMA, 2: SOMAC
DATE=`date +%d%m%Y_%H%M`;
DIR=$HOME/$PROT"_"$DATE;
mkdir $DIR;
# }}}

# Run {{{
./gr-somac/apps/container/config_interface_tuntap_"${IDS_CONFIG[$ARG_ID]}".sh;

pkill python; pkill ping;

RUN_TIME=7000
if [[ $ARG_ID -eq 9 ]]; then
	echo "COORDINATOR"
	echo $MODE > "/tmp/prot.txt"
	rm -rf "/tmp/backlog_file.npy"
	rm -rf "/tmp/out.log"
	((sleep $RUN_TIME; pkill python) & gr-somac/examples/wifi_transceiver_FlexDataLink_"${IDS_CONFIG[$ARG_ID]}".py);
else
	echo "NORMAL NODE"
	((sleep $RUN_TIME; pkill python; pkill ping) & gr-somac/examples/wifi_transceiver_FlexDataLink_"${IDS_CONFIG[$ARG_ID]}".py >/dev/null 2>&1 & python $HOME/gr-somac/apps/container/ping.py "${IDS_1[$ARG_ID]}" "${IDS_2[$ARG_ID]}");
fi
# }}}

# Copy logs {{{
cp /tmp/*npy $DIR;
cp /tmp/*log $DIR;
# }}}
