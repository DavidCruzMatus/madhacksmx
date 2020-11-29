#!/bin/bash
# Create the environment:
wget --quiet https://repo.anaconda.com/miniconda/Miniconda2-4.5.11-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc 
echo "export PATH=$PATH:/opt/conda/bin" >> ~/.bashrc
conda update -y -n base -c defaults conda
conda create -y --name madhacksmx -y python=3.7 tensorflow numpy PyYAML pip flask flask-socketio
conda init bash