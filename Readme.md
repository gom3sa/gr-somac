## About SOMAC
SOMAC is a Self-Organizing MAC-sublayer system. SOMAC switches MAC protocols in order to improve the overall network's performance. The MAC protocol selection engine is based on the Q-Learning algorithm.

The project is fully implemented in Software-Defined Radios (SDR), including both the data link layer (i.e. MAC protocols and framing) and the physical (PHY) layer.

## MAC Protocols
There are 2 MAC protocols available currently. They bellong to the project [gr-macprotocols](https://github.com/andreviniciusgsg/gr-macprotocols), click in the link for more information.

## PHY Layer
SOMAC uses the PHY layer from the project IEEE 802.11 a/g/p Transceiver. More information is available in [https://github.com/bastibl/gr-ieee802-11](https://github.com/bastibl/gr-ieee802-11).

## Upper layers
The upper layers can be either simulated by GNU Radio or connected to the upper layer of the linux operating system via TUN/TAP interfaces. Examples are provided for the latter, allowing the use of well-known applications such as ping, ftp, ssh, etc. to generate network traffic.

## Installation
There are two installation scripts available for SOMAC. The first is called *install-pc.sh* and relates to the installation over a physical machine or a virtual machine (both tested on Ubuntu 16.04 and Ubuntu 18.04). On the other hand, the second is called *install-container.sh* is designated for installation over an Ubuntu docker container. In both cases, the script checks for all SOMAC dependencies and installs the missing ones. That includes the list below.

* GNU Radio;
* cmake;
* git;
* [gr-ieee802-11](https://github.com/avgsg/gr-ieee802-11) (plus swig, liblog4cpp5-dev, and log4cpp);
* [gr-foo](https://github.com/bastibl/gr-foo);
* [gr-toolkit](https://github.com/avgsg/gr-toolkit);
* [gr-macprotocols](https://github.com/avgsg/gr-macprotocols);
* and gr-somac itself.

## Examples

#### TUN/TAP config scripts
There are necessary steps to configure the TUN/TAP interface in order to connect the upper layers from the linux operating system to the data link and PHY layers of SOMAC. The folder gr-somac/apps provides config scripts for that. The scripts *config_interface_tuntap_GATEWAY.sh* relates to the coordinator/master node, whereas *config_interface_tuntap_\<ID\>.sh* related to ordinary/slave nodes. The master node gets the following IP: 192.168.123.1 for the TUN/TAP interface. Others follow the increasing sequency 192.168.123.2, 192.168.123.3, ..., 192.168.123.n, where n+1 is equal to \<ID\>.

#### GNU Radio examples
Examples can be found at gr-somac/examples. Those scripts were tested using Software-Defined Radios USRP B2\*0 from the [FUTEBOL project, testbed UFMG](http://futebol.dcc.ufmg.br/). Some hyperparameters may need to be adjusted in order to run SOMAC on different devices.

## Author
Full name: André Vinícius Gomes Santos Gonçalves (usually André Gomes) <br />
E-mail: andre.gomes@dcc.ufmg.br <br />
Website: https://homepages.dcc.ufmg.br/~andre.gomes/