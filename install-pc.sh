#!/bin/bash

echo "Checking dependencies"
GNURADIO=`which gnuradio-companion`
CMAKE=`which cmake`
GIT=`which git`

if [ -z $GNURADIO]; then
  sudo apt -y install gnuradio
fi
if [ -z $CMAKE ]; then
  sudo apt -y install cmake
fi
if [ -z $GIT ]; then
  sudo apt -y install git
fi

echo "Installing gr-ieee802-11"

sudo apt -y install swig
sudo port install swig
sudo apt -y install liblog4cpp5-dev
sudo port install log4cpp
sudo apt -y install python-pip
export LC_ALL=C
sudo pip install scikit-learn
sudo pip install scipy

cd ~
sudo rm -rf gr-*

cd ~
git clone -b master https://github.com/bastibl/gr-foo.git
cd gr-foo
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig

cd ~
git clone -b master https://github.com/avgsg/gr-ieee802-11.git
cd gr-ieee802-11
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig

sudo sysctl -w kernel.shmmax=2147483648

cd ~
grcc ./gr-ieee802-11/examples/wifi_phy_hier.grc

echo "Installing gr-toolkit"

cd ~
git clone https://github.com/avgsg/gr-toolkit.git 
cd gr-toolkit 
mkdir build 
cd build
cmake .. 
sudo make install 
sudo ldconfig

echo "Installing gr-macprotocols"

cd ~
git clone https://github.com/avgsg/gr-macprotocols.git 
cd gr-macprotocols 
mkdir build 
cd build 
cmake .. 
make 
sudo make install 
sudo ldconfig

echo "Installing SOMAC (Self-Organizing MAC sublayer)"
cd ~
git clone https://github.com/avgsg/gr-somac.git
cd gr-somac
cd examples
cd ..
mkdir build
cd build
cmake ..
sudo make install
sudo ldconfig

cd ../examples
grcc ./data_link.grc

echo ""
echo "Done! You should be able to use gr-macprotocols based on gr-ieee802-11 right now. Please, report any problems <andre.gomes@dcc.ufmg.br>."
echo ""
