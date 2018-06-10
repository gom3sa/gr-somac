#!/bin/bash

echo "Configuration of tap interface."

# Which interface is this?
INTERFACE_ID="14"

MAC_LIST=("12:34:56:78:90:aa" "12:34:56:78:90:ab" "12:34:56:78:90:ac" "12:34:56:78:90:ad" "12:34:56:78:90:ae" "12:34:56:78:90:af" "12:34:56:78:90:ba" "12:34:56:78:90:bb" "12:34:56:78:90:bc" "12:34:56:78:90:bd" "12:34:56:78:90:be" "12:34:56:78:90:bf" "12:34:56:78:90:ca" "12:34:56:78:90:cb" "12:34:56:78:90:cc");
IP_LIST=("192.168.123.1" "192.168.123.2" "192.168.123.3" "192.168.123.4" "192.168.123.5" "192.168.123.6" "192.168.123.7" "192.168.123.8" "192.168.123.9" "192.168.123.10" "192.168.123.11" "192.168.123.12" "192.168.123.13" "192.168.123.14" "192.168.123.15");

GATEWAY_MAC=${MAC_LIST[0]}
GATEWAY_IP=${IP_LIST[0]}

MAC=${MAC_LIST[$INTERFACE_ID]}
IP=${IP_LIST[$INTERFACE_ID]}

if [[ $INTERFACE_ID -eq "0" ]]; then
	echo "Configuring Gateway interface.";

	sudo ip tuntap add dev tap0 user ${USER} mode tap; sleep 1

	sudo ifconfig tap0 down; sleep 1
	sudo ifconfig tap0 hw ether $MAC; sleep 1
	sudo ifconfig tap0 mtu 440; sleep 1
	sudo ifconfig tap0 up; sleep 1
	sudo ifconfig tap0 $IP; sleep 1

	sudo route del -net 192.168.123.0/24; sleep 1
	sudo route add -net 192.168.123.0/24 mss 400 dev tap0; sleep 1

	sudo tc qdisc del dev tap0 root; sleep 1
	sudo tc qdisc add dev tap0 root netem delay 10ms; sleep 1

	# Gateway knows IPs vs MACs of all nodes on the network
	count=1
	while [[ $count -le ${#MAC_LIST[@]} ]]; do
		sudo arp -s ${IP_LIST[$count]} ${MAC_LIST[$count]}
		count=$(( $count + 1 ));
	done
fi

if [[ ! $INTERFACE_ID -eq "0" ]]; then 
	echo "Configuring normal node, addr = ${MAC_LIST[$INTERFACE_ID]}."

	sudo ip tuntap add dev tap0 user ${USER} mode tap; sleep 1

	sudo ifconfig tap0 down; sleep 1
	sudo ifconfig tap0 hw ether $MAC; sleep 1
	sudo ifconfig tap0 mtu 440; sleep 1
	sudo ifconfig tap0 up; sleep 1
	sudo ifconfig tap0 $IP; sleep 1

	sudo route del -net 192.168.123.0/24; sleep 1
	sudo route add -net 192.168.123.0/24 mss 400 dev tap0; sleep 1

	sudo tc qdisc del dev tap0 root; sleep 1
	sudo tc qdisc add dev tap0 root netem delay 10ms; sleep 1

	sudo arp -s $GATEWAY_IP $GATEWAY_MAC
fi

echo ""
echo "Configuration is done! Check for any errors above."
echo ""
