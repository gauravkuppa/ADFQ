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
#RUN python3.6 -m 
#pip install wheel

#RUN python3.6 -m 
#source setup

#pip install pyyaml==5.4.1 scipy numpy tabulate matplotlib gym[atari,classic_control] tqdm joblib zmq dill progressbar2 mpi4py cloudpickle click opencv-python wandb filterpy scikit-image
#export MPLBACKEND=TKAgg

#RUN python3.6 -m 
#pip install 
#WORKDIR /tmp/
