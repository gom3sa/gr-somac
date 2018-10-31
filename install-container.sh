#!/bin/bash

echo "Checking dependencies"
GNURADIO=`which gnuradio-companion`
CMAKE=`which cmake`
GIT=`which git`
IP=`which ip`
PING=`which ping`
IFCONFIG=`which ifconfig`

if [ -z $GNURADIO]; then
	apt -y install gnuradio
fi
if [ -z $CMAKE ]; then
	apt -y install cmake
fi
if [ -z $GIT ]; then
	apt -y install git
fi
if [ -z $IP ]; then
	apt -y install iproute2
fi
if [ -z $PING ]; then
	apt -y install iputils-ping
fi
if [ -z $IFCONFIG ]; then
	apt -y install net-tools
fi


echo "Installing gr-ieee802-11"

apt -y install swig
port install swig
apt -y install liblog4cpp5-dev
port install log4cpp
apt -y install python-pip
export LC_ALL=C
pip install scikit-learn
pip install scipy

cd ~
git clone -b master https://github.com/bastibl/gr-foo.git
cd gr-foo
mkdir build
cd build
cmake ..
make
make install
ldconfig

cd ~
git clone -b master https://github.com/avgsg/gr-ieee802-11.git
cd gr-ieee802-11
mkdir build
cd build
cmake ..
make
make install
ldconfig

sysctl -w kernel.shmmax=2147483648

cd ~
grcc ./gr-ieee802-11/examples/wifi_phy_hier.grc

echo "Installing gr-toolkit"

cd ~
git clone https://github.com/avgsg/gr-toolkit.git 
cd gr-toolkit 
mkdir build 
cd build
cmake .. 
make install 
ldconfig

echo "Installing gr-macprotocols"

cd ~
git clone https://github.com/avgsg/gr-macprotocols.git 
cd gr-macprotocols 
mkdir build 
cd build 
cmake .. 
make 
make install 
ldconfig

echo "Installing SOMAC (Self-Organizing MAC sublayer)"
cd ~
git clone https://github.com/avgsg/gr-somac.git
cd gr-somac
cd examples
cd ..
mkdir build
cd build
cmake ..
make install
ldconfig

cd ../examples
grcc ./data_link.grc
#grcc ./gaussian_traffic_gen.grc
#grcc ./data_link_trafficgen.grc

echo ""
echo "Done! You should be able to use gr-macprotocols based on gr-ieee802-11 right now. Please, report any problems <andre.gomes@dcc.ufmg.br>."
echo ""