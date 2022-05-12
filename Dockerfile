FROM nvidia/cuda:9.0-cudnn7-devel-ubuntu16.04

RUN apt-get -y update &&  && apt-get -y install  python-dev python3-dev  python-pip python3-pip 
RUN apt-get update && \
  apt-get -y upgrade && \
  apt-get install -y software-properties-common

RUN apt-get install -y build-essential sudo git wget libopenmpi-dev python3.6 python3.6-dev python3-pip python3.6-venv zlib1g-dev cmake python-opencv tmux libav-tools vim

# update pip
RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel

RUN python3.6 -m pip install tensorflow-gpu pyyaml scipy numpy tabulate matplotlib
RUN python3.6 -m pip install gym[atari,classic_control] tqdm joblib zmq dill progressbar2 mpi4py cloudpickle click opencv-python

WORKDIR /tmp/

RUN export uid=1008 gid=1008 && \
    mkdir -p /home/developer && \
    echo "developer:x:${uid}:${gid}:Developer,,,:/home/developer:/bin/bash" >> /etc/passwd && \
    echo "developer:x:${uid}:" >> /etc/group && \
    echo "developer ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/developer && \
    chmod 0440 /etc/sudoers.d/developer && \
    chown ${uid}:${gid} -R /home/developer

USER developer

ENV HOME /home/developer/Desktop/docker-code/
WORKDIR /home/developer/Desktop/docker-code/
