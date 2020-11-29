#!/bin/bash
conda activate madhacksmx
conda install -y -n madhacksmx -c conda-forge -y imutils opencv cx_oracle
# Activate oracle lib:
apt update
apt-get install -y libaio-dev libgl1-mesa-glx 
sh -c "echo /root/oracle/instantclient_19_9 > /etc/ld.so.conf.d/oracle-instantclient.conf"
ldconfig
apt-get install -y git
