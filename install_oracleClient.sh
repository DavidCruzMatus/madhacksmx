#!/bin/bash
apt-get update
apt-get install -y zip
unzip /root/oracle/instantclient-basic-linux.x64-19.6.0.0.0dbru.zip
echo "export PATH=$PATH:/root/oracle/instantclient_19_9" >> ~/.bashrc
echo "export TNS_ADMIN=/root/oracle/instantclient_19_9/network/admin" >> ~/.bashrc
echo "export LD_LIBRARY_PATH=/root/oracle/instantclient_19_9" >> ~/.bashrc