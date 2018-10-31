#!/bin/bash

cd ~
apt install net-tools
apt install iproute2

cd ~
rm -rf gr-somac

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
