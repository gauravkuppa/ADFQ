FROM nvidia/cuda:11.6.0-base-ubuntu20.04
ARG DEBIAN_FRONTEND=noninteractive

#ROS-Setup
RUN apt-get update \
    && apt-get install -y \
      build-essential \
      cmake \
      cppcheck \
      gdb \
      git \
      lsb-release \
      software-properties-common \
      sudo \
      neovim \
      wget \
      net-tools \
      iputils-ping \
      tmux \
      locales \
      python3-pip \
      curl \
      vim \
      ffmpeg\
    && apt-get clean

# Conda setup
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -b -p /miniconda
ENV PATH=$PATH:/miniconda/condabin:/miniconda/bin

ENV DEBIAN_FRONTEND=noninteractive
RUN DEBIAN_FRONTEND=noninteractive apt-get install keyboard-configuration
RUN sudo apt-get update \
    && sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list' \
    && curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add - \
    && sudo apt-get update \
    && sudo apt-get install -y \
      python3-catkin-tools \
      python3-rosdep \
      python3-rosinstall \
      python3-vcstool \
      ros-noetic-catkin \
      ros-noetic-rosbash \
      ros-noetic-desktop \
      ros-noetic-pcl-ros \
      ros-noetic-tf2-geometry-msgs \
    && sudo rosdep init \
    && rosdep update



RUN conda init

WORKDIR /home

#RUN apt-get install -y build-essential sudo git wget libopenmpi-dev python3.6 python3.6-dev python3-pip python3.6-venv zlib1g-dev cmake python-opencv tmux libav-tools vim

# update pip
#RUN python3.6 -m pip install pip --upgrade
#RUN python3.6 -m pip install wheel

#RUN python3.6 -m pip install tensorflow-gpu pyyaml scipy numpy tabulate matplotlib
#RUN python3.6 -m pip install gym[atari,classic_control] tqdm joblib zmq dill progressbar2 mpi4py cloudpickle click opencv-python

#WORKDIR /tmp/

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
