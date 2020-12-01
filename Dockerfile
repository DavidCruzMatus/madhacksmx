# https://www.youtube.com/watch?v=MAjbzx2zq-c
FROM continuumio/miniconda3



# Create the environment:

COPY . /social

WORKDIR /social



# Initialize conda in bash config fiiles:

SHELL ["/bin/bash", "--login", "-c"]

RUN conda update -n base -c defaults conda

RUN conda create --name madhacksmx -y python=3.7 tensorflow numpy PyYAML pip flask flask-socketio

RUN conda install -n madhacksmx -c conda-forge -y imutils opencv cx_oracle

RUN conda init bash

RUN conda activate madhacksmx



# Install oracle lib:

#RUN apt update

#RUN apt-get install -y libaio-dev libgl1-mesa-glx

RUN sh -c "echo $HOME/social/oralib > /etc/ld.so.conf.d/oracle-instantclient.conf"

RUN ldconfig

RUN export LD_LIBRARY_PATH=$HOME/social/oralib:$LD_LIBRARY_PATH



# Activate the environment, and make sure it's activated:

RUN echo "conda activate madhacksmx" >> ~/.bashrc

RUN echo "export ORACLE_HOME=/social/oralib" >> ~/.bashrc

RUN echo "ldconfig" >> ~/.bashrc

RUN echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME" >> ~/.bashrc

#RUN echo "export QT_QPA_PLATFORM=offscreen" >> ~/.bashrc

RUN echo "export FLASK_APP=stream_social_distance_v1.py" >> ~/.bashrc



EXPOSE 5000

ENTRYPOINT flask run --host=0.0.0.0



#CMD [ "/bin/bash" ]

#sudo docker build -t madhacksmx .

#sudo docker run -p 5000:5000 madhacksmx flask run --host=0.0.0.0
#export QT_QPA_PLATFORM=eglfs, minimal, minimalegl, offscreen, vnc, xcb