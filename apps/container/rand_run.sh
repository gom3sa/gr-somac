#!/bin/bash

ARG_ID=$1
MODE=$2
RANDPROFILE=$3

# IDs of TunTap script
IDS_CONFIG=(1 2 3 4 5 6 7 8 9 GATEWAY)

# Setup {{{
PROT=$MODE; # 0: CSMA, 1: TDMA, 2: SOMAC
DATE=`date +%d%m%Y_%H%M`;
DIR=$HOME/$PROT"_"$RANDPROFILE"_"$DATE;
mkdir $DIR;
# }}}

cp "$HOME/gr-somac/data/30/profile_$RANDPROFILE.npy" /tmp/profile.npy

# Run {{{
cd ~
./gr-somac/apps/container/config_interface_tuntap_"${IDS_CONFIG[$ARG_ID]}".sh;

pkill python; pkill ping;

RUN_TIME=2700
if [[ $ARG_ID -eq 9 ]]; then
	echo "COORDINATOR"
	if [[ $MODE -eq 5 ]]; then
		if [[ $(( RANDOM % 2 )) -eq 0 ]]; then 
			echo 0 > "/tmp/init_prot.txt"
		else 
			echo 1 > "/tmp/init_prot.txt"
		fi
	fi

	echo $MODE > "/tmp/prot.txt"
	rm -rf "/tmp/backlog_file.npy"
	rm -rf "/tmp/out.log"
	((sleep $RUN_TIME; pkill python) & ./gr-somac/examples/wifi_transceiver_FlexDataLink_"${IDS_CONFIG[$ARG_ID]}".py);
else
	echo "NORMAL NODE"
	((sleep $RUN_TIME; pkill python; pkill ping) & ./gr-somac/examples/wifi_transceiver_FlexDataLink_"${IDS_CONFIG[$ARG_ID]}".py >/dev/null 2>&1 & python $HOME/gr-somac/apps/container/rand_ping.py "${IDS_CONFIG[$ARG_ID]}");
fi
# }}}

# Copy logs {{{
cp /tmp/*npy $DIR;
cp /tmp/*log $DIR;
# }}}
