#!/bin/bash

cd ~
apt -y install net-tools
apt -y install iproute2
apt -y install iputils-ping

cd ~
rm -rf gr-somac

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
